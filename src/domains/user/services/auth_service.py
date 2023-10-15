from typing import Any, List, Dict
from ....routers.req.authorization import gen_token
from ..value_objects.auth_vo import *
from ...cache import ICache
from ...service_api import IServiceApi
from ....infra.utils.util import gen_confirm_code
from ....infra.utils.time_util import gen_timestamp
from ....configs.conf import SHORT_TERM_TTL, LONG_TERM_TTL,\
    MY_STATUS_OF_COMPANY_APPLY, STATUS_OF_COMPANY_APPLY,\
    MY_STATUS_OF_TEACHER_APPLY, STATUS_OF_TEACHER_APPLY
from ....configs.constants import PATHS, PREFETCH
from ....configs.region_hosts import get_auth_region_host, get_match_region_host
from ....configs.exceptions import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class AuthService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache

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

    def confirm_signup(self, host: str, body: SignupConfirmVO):
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
                                        })

        role_id_key = str(auth_res["role_id"])
        auth_res = self.__apply_token(auth_res)
        updated = self.cache.set(
            role_id_key, auth_res, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f"AuthService.confirm_signup:[cache set],\
                role_id_key:%s, auth_res:%s, ex:%s, cache data:%s",
                role_id_key, auth_res, LONG_TERM_TTL, updated)
            raise ServerException(msg="server_error")
        else:
            return {"auth": auth_res}

    def __verify_confirmcode(self, confirm_code: str, user: Any):
        if not user or not "confirm_code" in user:
            raise NotFoundException(msg="no signup data")

        if user == {}:
            raise DuplicateUserException(msg="registering")

        if confirm_code != str(user["confirm_code"]):
            raise ClientException(msg="wrong confirm_code")

    def __apply_token(self, res: Dict):
        # gen jwt token
        token = gen_token(res, ["region", "role_id", "role"])
        res.update({"token": token})
        return res

    """
    login
    """

    def login(self, auth_host: str, match_host: str, body: LoginVO):
        # request login & auth data
        region = None
        auth_res = None
        try:
            auth_res = self.__req_login(auth_host, body)
            
        except ForbiddenException as err_payload:
            # found in S3, and region != "current_region"(在 meta, 解密後才會知道)(找錯地方)
            # S3 有記錄但該地區的 auth-service 沒記錄，auth 從 S3 找 region 後回傳
            log.warn("WRONG REGION: \n \
                    has record in S3, but no record in DB of current region, ready to request user record from register region")
            log.error(f"AuthService.login fail: [request res: WRONG REGION], \
                auth_host:%s, match_host:%s, body:%s, region:%s, auth_res:%s, err_payload:%s", 
                auth_host, match_host, body, region, auth_res, err_payload.msg)
                
            try:
                email_info = err_payload.data
                region = email_info["region"]  # 換其他 region 再請求一次
                auth_host = get_auth_region_host(region)
                match_host = get_match_region_host(region)
                auth_res = self.__req_login(auth_host, body)
                
            except Exception as redirect_err:
                log.error(f"AuthService.login fail: [redirect_fail], \
                    auth_host:%s, match_host:%s, body:%s, region:%s, auth_res:%s, err:%s", 
                    auth_host, match_host, body, region, auth_res, redirect_err.__str__())
                raise ServerException(msg="redirect_fail")
        
        except Exception as e:
            log.error(f"AuthService.login fail: [unknow_error], \
                auth_host:%s, match_host:%s, body:%s, region:%s, auth_res:%s, err:%s", 
                auth_host, match_host, body, region, auth_res, e.__str__())
            raise ServerException(msg="unknow_error")

        # cache auth data
        role_id_key = str(auth_res["role_id"])
        auth_res = self.__apply_token(auth_res)
        auth_res.update({
            "current_region": body.current_region,
            "socketid": "it's socketid",
            "online": True,
        })
        self.__cache_auth_res(role_id_key, auth_res)

        # request match data
        role_path = PATHS[auth_res["role"]]
        size = body.prefetch or PREFETCH
        match_res = self.__req_match_data(
            match_host, role_path, role_id_key, size)

        return {
            "auth": auth_res,
            "match": match_res,
        }

    def __req_login(self, auth_host: str, body: LoginVO):
        return self.req.simple_post(
            f"{auth_host}/login", json=body.dict())
        

    def __cache_auth_res(self, role_id_key: str, auth_res: Dict):
        updated = self.cache.set(
            role_id_key, auth_res, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f"AuthService.__cache_auth_res fail: [cache set],\
                role_id_key:%s, auth_res:%s, ex:%s, cache data:%s",
                role_id_key, auth_res, LONG_TERM_TTL, updated)
            raise ServerException(msg="server_error")

    def __req_match_data(self, match_host: str, role_path: str, role_id_key: str, size: int):
        my_statuses, statuses = [], []
        
        if role_path == "companies" or role_path == "company":
            my_statuses = MY_STATUS_OF_COMPANY_APPLY
            statuses = STATUS_OF_COMPANY_APPLY
        elif role_path == "teachers" or role_path == "teacher":
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

    def logout(self, role_id: int, token: str):
        role_id_key = str(role_id)
        user = self.__cache_check_for_auth(role_id_key, token)
        user_logout_status = self.__logout_status(user)

        # "LONG_TERM_TTL" for redirct notification
        self.__cache_logout_status(role_id_key, user_logout_status)
        return (None, "successfully logged out")

    def __cache_check_for_auth(self, role_id_key: str, token: str):
        user = self.cache.get(role_id_key)

        if not user or not "token" in user:
            raise ClientException(msg="logged out")

        if user["token"] != token:
            raise UnauthorizedException(msg="invalid user")

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
    def send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr, ):
        verify_token = self.__req_send_reset_password_comfirm_email(auth_host, email)
        self.cache.set(verify_token, email, SHORT_TERM_TTL)
        return 'send_email_success'

    def reset_passwrod(self, auth_host: str, verify_token: str, body: ResetPasswordVO):
        checked_email = self.cache.get(verify_token)
        if not checked_email:
            raise ServerException(msg="invalid token") 
        if checked_email != body.register_email:
            raise ServerException(msg="invalid user")
        auth_res = self.__req_reset_password(auth_host, body)
        self.cache.delete(verify_token)
        return {'auth_res': auth_res}

    def update_password(self, auth_host: str, token: str, role_id: int, body: UpdatePasswordVO):
        # check is in login status
        _ = self.__cache_check_for_auth(str(role_id), token)
        auth_res = self.__req_update_password(auth_host, body)
        return {'auth_res': auth_res}

    def __req_send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr):
        return self.req.simple_get(
            f"{auth_host}/password/send_reset_password_confirm_email", params={'email': email}) 

    def __req_update_password(self, auth_host: str, body: UpdatePasswordVO):
        return self.req.simple_post(
            f"{auth_host}/password/update", json=body.dict())

    def __req_reset_password(self, auth_host: str, body: ResetPasswordVO):
        return self.req.simple_post(
            f"{auth_host}/password/update", json=body.dict()) 