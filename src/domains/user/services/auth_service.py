from typing import Any, List, Dict
from ....routers.req.authorization import gen_token
from ..value_objects.auth_vo import *
from ...cache import ICache
from ...service_api import IServiceApi
from ....infra.utils.util import gen_confirm_code
from ....infra.utils.time_util import gen_timestamp
from ....configs.conf import *
from ....configs.constants import PATHS, PREFETCH, COM, TEACH
from ....configs.region_hosts import get_auth_region_host, get_match_region_host
from ....configs.exceptions import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class AuthService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache

    '''
    grant refreshed token & new access token
    TODO: copy table: 'account_indexs'(jp) to other regions(ge, us, ...etc);
    'account_indexs' schema: role_id(partition key), aid, srt_ts, ext_ts, others...
    '''
    def grant_refresh_token(self, host: str, body: AuthUpdateTokenDTO, current_region: str) -> (Optional[GrantTokenVO]):
        # 會到這裡表示用戶的 token 已經過期，只能透過 role_id 和 refresh_token 來驗證用戶;
        # 同時傳送 gateway 端的 expired_ts 給 auth-service 取得新的 refresh token
        # FIXME: 2024/02/05 implement refresh-token API as following
        # refresh_token_res = self.req.simple_post(f'{host}/security/refresh-token', json=body.dict())
        refresh_token_res = {"refresh_token": "new refresh token"}

        # 假設 gateway & auth-service 的時間差異不大(誤差幾分鐘)
        current_user = {
            'role': body.role,
            'role_id': body.role_id,
            'region': current_region,
        }
        current_user = self.apply_token(current_user, body.expired_ts)
        refresh_token_res['token'] = current_user['token']
        return {'auth': refresh_token_res}

    """
    get_public_key
    """

    def get_public_key(self, host: str):
        timestamp = gen_timestamp()
        slot = timestamp % 100
        pubkey = self.cache.get(f"pubkey_{slot}")
        if not pubkey:
            pubkey = self.req.simple_get(f"{host}/security/pubkey", params={"ts": timestamp})
            self.cache.set(f"pubkey_{slot}", pubkey, ex=LONG_TERM_TTL)

        return {"pubkey": pubkey}

    """
    signup
    """

    def signup(self, host: str, body: SignupVO):
        email = body.email
        meta = body.meta
        self.__cache_check_for_duplicates(email)

        confirm_code = gen_confirm_code()
        auth_res = self.__req_send_confirmcode_by_email(
            host, email, confirm_code)

        if auth_res == "email_sent":
            self.__cache_confirmcode(email, confirm_code, meta)

            # FIXME: remove the res here('confirm_code') during production
            return {
                "for_testing_only": confirm_code
            }

        else:
            self.cache.set(email, {"avoid_freq_email_req_and_hit_db": 1}, SHORT_TERM_TTL)
            raise DuplicateUserException(msg="email_registered")

    def __cache_check_for_duplicates(self, email: str):
        data = self.cache.get(email)
        if data:
            log.error(f"AuthService.__cache_check_for_duplicates:[business error],\
                email:%s, cache data:%s", email, data)
            raise DuplicateUserException(msg="registered or registering")

    def __req_send_confirmcode_by_email(self, host: str, email: str, confirm_code: str):
        auth_res, msg, err = self.req.post(f"{host}/sendcode/email", json={
            "email": email,
            "confirm_code": confirm_code,
            "sendby": "no_exist",  # email 不存在時寄送
        })
        
        if msg or err:
            log.error(f"AuthService.__req_send_confirmcode_by_email:[request exception], \
                host:%s, email:%s, confirm_code:%s, auth_res:%s, msg:%s, err:%s",
                host, email, confirm_code, auth_res, msg, err)
            self.cache.set(email, {"avoid_freq_email_req_and_hit_db": 1}, SHORT_TERM_TTL)

        return auth_res

    def __cache_confirmcode(self, email: str, confirm_code: str, meta: str):
        email_playload = {
            "email": email,
            "confirm_code": confirm_code,
            "meta": meta,
        }
        self.cache.set(email, email_playload, ex=SHORT_TERM_TTL)

    """
    confirm_signup
    """

    def confirm_signup(self, host: str, body: AuthSignupVO):
        # body = body.gen_ext()
        email = body.email
        confirm_code = body.confirm_code
        user = self.cache.get(email)
        self.__verify_confirmcode(confirm_code, user)

        # "registering": empty data, but TTL=30sec
        self.cache.set(email, {}, ex=30)
        auth_res = self.req.simple_post(f"{host}/signup",
                                        json={
                                            "email": email,
                                            # "meta": "{\"role\":\"teacher\",\"pass\":\"secret\"}"
                                            "meta": user["meta"],
                                            "pubkey": body.pubkey,
                                            "expired_ts": body.expired_ts,
                                        })

        role_id_key = str(auth_res["role_id"])
        self.cache_auth_res(role_id_key, auth_res)
        auth_res = self.apply_token(auth_res, body.expired_ts)
        return {"auth": auth_res}

    def __verify_confirmcode(self, confirm_code: str, user: Any):
        if not user or not "confirm_code" in user:
            raise NotFoundException(msg="no signup data")

        if user == {}:
            raise DuplicateUserException(msg="registering")

        if confirm_code != str(user["confirm_code"]):
            raise ClientException(msg="wrong confirm_code")

    def apply_token(self, res: Dict, expired_timestamp: float = None):
        # gen jwt token
        token = gen_token(
            res,
            ["region", "role_id", "role"],
            expired_timestamp,
        )
        res.update({"token": token})
        return res

    """
    login
    """

    def login(self, auth_host: str, match_host: str, body: AuthLoginVO):
        # body = body.gen_ext()
        # request login & auth data
        (auth_res, region) = self.__req_login_or_register_region(auth_host, match_host, body)
        if auth_res is None:
            auth_host = get_auth_region_host(region)
            match_host = get_match_region_host(region)
            auth_res = self.__req_login(auth_host, body)

        # cache auth data
        role_id_key = str(auth_res["role_id"])
        auth_res.update({
            "current_region": body.current_region,
            "socketid": "it's socketid",
        })
        self.cache_auth_res(role_id_key, auth_res)
        auth_res = self.apply_token(auth_res, body.expired_ts)

        # request match data
        role_path = PATHS[auth_res["role"]]
        match_res = self.req_match_data(
            match_host,
            role_path,
            role_id_key,
            body.prefetch
        )

        return {
            "auth": auth_res,
            "match": match_res,
        }
        
    def __req_login_or_register_region(self, auth_host: str, match_host: str, body: AuthLoginVO):
        register_region = None
        auth_res = None
        try:
            auth_res = self.__req_login(auth_host, body)
            return (auth_res, None)
            
        except ForbiddenException as exp_payload:
            # found in S3, and region != "current_region"(在 meta, 解密後才會知道)(找錯地方)
            # S3 有記錄但該地區的 auth-service 沒記錄，auth 從 S3 找 region 後回傳
            log.error(f"AuthService.login fail: [WRONG REGION: there is the user record in S3, \
                but no record in the DB of current region, it's ready to request the user record from register region], \
                auth_host:%s, match_host:%s, body:%s, register_region:%s, auth_res:%s, exp_payload:%s", 
                auth_host, match_host, body, register_region, auth_res, exp_payload.msg)
                
            try:
                email_info = exp_payload.data
                register_region = email_info["region"]  # 換其他 region 再請求一次
                return (None, register_region)
                
            except Exception as format_err:
                log.error(f"AuthService.login fail: [exp_payload format_err], \
                    auth_host:%s, match_host:%s, body:%s, auth_res:%s, exp_payload:%s, format_err:%s", 
                    auth_host, match_host, body, auth_res, exp_payload, format_err.__str__())
                raise ServerException(msg="format_err")
            
        except Exception as e:
            log.error(f"AuthService.login fail: [unknow_error], \
                auth_host:%s, match_host:%s, body:%s, register_region:%s, auth_res:%s, err:%s", 
                auth_host, match_host, body, register_region, auth_res, e.__str__())
            raise_http_exception(e, 'unknow_error')
        

    def __req_login(self, auth_host: str, body: AuthLoginVO):
        return self.req.simple_post(
            f"{auth_host}/login", json=body.dict())
        

    def cache_auth_res(self, role_id_key: str, auth_res: Dict):
        auth_res.update({
            "online": True,
        })
        updated = self.cache.set(
            role_id_key, auth_res, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f"AuthService.__cache_auth_res fail: [cache set],\
                role_id_key:%s, auth_res:%s, ex:%s, cache data:%s",
                role_id_key, auth_res, LONG_TERM_TTL, updated)
            raise ServerException(msg="server_error")

    def req_match_data(self, match_host: str, role_path: str, role_id_key: str, size: int = PREFETCH):
        my_statuses, statuses = [], []
        
        if role_path in COM:
            my_statuses = MY_STATUS_OF_COMPANY_APPLY
            statuses = STATUS_OF_COMPANY_APPLY
        elif role_path in TEACH:
            my_statuses = MY_STATUS_OF_TEACHER_APPLY
            statuses = STATUS_OF_TEACHER_APPLY
            
        match_res = self.req.simple_get(
            url=f"{match_host}/{role_path}/{role_id_key}/matchdata",
            params={
                "size": size,
                "my_statuses": my_statuses,
                "statuses": statuses,
            }
        )

        return match_res

    """
    logout
    """

    def logout(self, role_id: int):
        role_id_key = str(role_id)
        user = self.__cache_check_for_auth(role_id_key)
        user_logout_status = self.__logout_status(user)

        # "LONG_TERM_TTL" for redirct notification
        self.__cache_logout_status(role_id_key, user_logout_status)
        return (None, "successfully logged out")
    
    @staticmethod
    def is_login(cache: ICache, visitor: BaseAuthDTO = None) -> (bool):
        if visitor is None:
            return False

        role_id_key = str(visitor.role_id)
        user: Dict = cache.get(role_id_key)
        if user is None:
            return False

        return user.get("online", False) and \
            user.get("role", None) == visitor.role

    def __cache_check_for_auth(self, role_id_key: str):
        user = self.cache.get(role_id_key)
        if not user or not user.get("online", False):
            raise ClientException(msg="logged out")

        return user

    def __logout_status(self, user: Dict):
        role_id = user["role_id"]
        region = user["region"]
        current_region = user["current_region"]

        return {
            "role_id": role_id,
            "region": region,
            "current_region": current_region,
            "online": False,
        }

    def __cache_logout_status(self, role_id_key: str, user_logout_status: Dict):
        updated = self.cache.set(
            role_id_key, user_logout_status, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f"AuthService.__cache_logout_status fail: [cache set],\
                role_id_key:%s, user_logout_status:%s, ex:%s, cache data:%s",
                role_id_key, user_logout_status, LONG_TERM_TTL, updated)
            raise ServerException(msg="server_error")

    '''
    password
    '''
    def send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr):
        self.__cache_check_for_reset_password(email)
        data = self.__req_send_reset_password_comfirm_email(auth_host, email)
        self.__cache_token_by_reset_password(data['token'], email)
        #TEST: log
        return f'''send_email_success {data['token']}'''

    def reset_passwrod(self, auth_host: str, verify_token: str, body: ResetPasswordVO):
        checked_email = self.cache.get(verify_token)
        if not checked_email:
            raise UnauthorizedException(msg="invalid token") 
        if checked_email != body.register_email:
            raise UnauthorizedException(msg="invalid user")
        self.__req_reset_password(auth_host, body)
        self.__cache_remove_by_reset_password(verify_token, checked_email)

    
    def __cache_check_for_reset_password(self, email: EmailStr):
        data = self.cache.get(f'{email}:reset_pw')
        if data:
            log.error(f"AuthService.__cache_check_for_reset_password:[too many reqeusts error],\
                email:%s, cache data:%s", email, data)
            raise TooManyRequestsException(msg="frequent_requests")
    
    def __cache_token_by_reset_password(self, verify_token: str, email: EmailStr):
        self.cache.set(f'{email}:reset_pw', '1', REQUEST_INTERVAL_TTL)
        self.cache.set(verify_token, email, SHORT_TERM_TTL)
        
    def __cache_remove_by_reset_password(self, verify_token: str, email: EmailStr):
        self.cache.delete(f'{email}:reset_pw')
        self.cache.delete(verify_token)
        

    def update_password(self, auth_host: str, role_id: int, body: UpdatePasswordVO):
        self.__cache_check_for_email_validation(role_id, body.register_email)
        self.__req_update_password(auth_host, body)

    def __req_send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr):
        return self.req.simple_get(
            f"{auth_host}/password/reset/email", params={'email': email}) 

    def __cache_check_for_email_validation(self, role_id: int, register_email: EmailStr):
        role_id_key = str(role_id)
        data = self.cache.get(role_id_key)
        if not 'email' in data or str(register_email) != data['email']:
            raise UnauthorizedException(msg='invalid email')

    def __req_update_password(self, auth_host: str, body: UpdatePasswordVO):
        return self.req.simple_put(
            f"{auth_host}/password/update", json=body.dict())

    def __req_reset_password(self, auth_host: str, body: ResetPasswordVO):
        return self.req.simple_put(
            f"{auth_host}/password/update", json=body.dict()) 