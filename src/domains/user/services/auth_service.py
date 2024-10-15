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
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AuthService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache

    """
    get_public_key
    """

    async def get_public_key(self, host: str):
        timestamp = gen_timestamp()
        slot = timestamp % 100
        pubkey = await self.cache.get(f"pubkey_{slot}")
        if not pubkey:
            pubkey = await self.req.simple_get(f"{host}/security/pubkey", params={"ts": timestamp})
            await self.cache.set(f"pubkey_{slot}", pubkey, ex=LONG_TERM_TTL)

        return {"pubkey": pubkey}

    """
    signup
    """

    async def signup(self, host: str, body: SignupVO):
        email = body.email
        meta = body.meta
        confirm_code = None
        auth_res = None

        try:
            await self.__cache_check_for_frequency(email)
            confirm_code = gen_confirm_code()
            auth_res = await self.__req_send_confirmcode_by_email(
                host, email, confirm_code)

            await self.__cache_confirmcode(email, confirm_code, meta)

            # FIXME: remove the res here('confirm_code') during production
            return {
                "for_testing_only": confirm_code
            }
        
        except Exception as e:
            log.error(f"AuthService.signup:[request exception], \
                host:%s, email:%s, confirm_code:%s, auth_res:%s, err:%s",
                host, email, confirm_code, auth_res, e)
            raise_http_exception(e=e, msg=e.msg if e.msg else 'unknow_error')


    async def __cache_check_for_frequency(self, email: str):
        data = await self.cache.get(email)
        if data:
            log.error(f"AuthService.__cache_check_for_frequency:[too many request error],\
                email:%s, cache data:%s", email, data)
            raise TooManyRequestsException(msg="frequently request")

        await self.cache.set(email, {"avoid_freq_email_req_and_hit_db": 1}, SHORT_TERM_TTL)

    async def __req_send_confirmcode_by_email(self, host: str, email: str, confirm_code: str):
        auth_res = await self.req.simple_post(f"{host}/sendcode/email", json={
            "email": email,
            "confirm_code": confirm_code,
            "sendby": "no_exist",  # email 不存在時寄送
        })

        return auth_res

    async def __cache_confirmcode(self, email: str, confirm_code: str, meta: str):
        email_playload = {
            "email": email,
            "confirm_code": confirm_code,
            "meta": meta,
        }
        await self.cache.set(email, email_playload, ex=SHORT_TERM_TTL)

    """
    confirm_signup
    """

    async def confirm_signup(self, host: str, body: SignupConfirmVO):
        email = body.email
        confirm_code = body.confirm_code
        user = await self.cache.get(email)
        self.__verify_confirmcode(confirm_code, user)

        # "registering": empty data, but TTL=30sec
        await self.cache.set(email, {}, ex=30)
        auth_res = await self.req.simple_post(f"{host}/signup",
                                        json={
                                            "email": email,
                                            # "meta": "{\"role\":\"teacher\",\"pass\":\"secret\"}"
                                            "meta": user["meta"],
                                            "pubkey": body.pubkey,
                                        })

        role_id_key = str(auth_res["role_id"])
        await self.cache_auth_res(role_id_key, auth_res)
        auth_res = self.apply_token(auth_res)
        return {"auth": auth_res}

    def __verify_confirmcode(self, confirm_code: str, user: Any):
        if not user or not "confirm_code" in user:
            raise NotFoundException(msg="no signup data")

        if user == {}:
            raise DuplicateUserException(msg="registering")

        if confirm_code != str(user["confirm_code"]):
            raise ClientException(msg="wrong confirm_code")

    def apply_token(self, res: Dict):
        # gen jwt token
        token = gen_token(res, ["region", "role_id", "role"])
        res.update({"token": token})
        return res

    """
    login
    """

    async def login(self, auth_host: str, match_host: str, body: LoginVO):
        # request login & auth data
        (auth_res, region) = await self.__req_login_or_register_region(auth_host, match_host, body)
        if auth_res is None:
            auth_host = get_auth_region_host(region)
            match_host = get_match_region_host(region)
            auth_res = await self.__req_login(auth_host, body)

        # cache auth data
        role_id_key = str(auth_res["role_id"])
        auth_res.update({
            "current_region": body.current_region,
        })
        await self.cache_auth_res(role_id_key, auth_res)
        auth_res = self.apply_token(auth_res)

        # request match data
        role_path = PATHS[auth_res["role"]]
        match_res = await self.req_match_data(
            match_host,
            role_path,
            role_id_key,
            body.prefetch
        )

        return {
            "auth": auth_res,
            "match": match_res,
        }
        
    async def __req_login_or_register_region(self, auth_host: str, match_host: str, body: LoginVO):
        register_region = None
        auth_res = None
        try:
            auth_res = await self.__req_login(auth_host, body)
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
            raise_http_exception(e, e.msg if e.msg else 'unknow_error')
        

    async def __req_login(self, auth_host: str, body: LoginVO):
        return await self.req.simple_post(
            f"{auth_host}/login", json=body.dict())
        

    async def cache_auth_res(self, role_id_key: str, auth_res: Dict):
        auth_res.update({
            "online": True,
        })
        updated = await self.cache.set(
            role_id_key, auth_res, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f"AuthService.__cache_auth_res fail: [cache set],\
                role_id_key:%s, auth_res:%s, ex:%s, cache data:%s",
                role_id_key, auth_res, LONG_TERM_TTL, updated)
            raise ServerException(msg="server_error")

    async def req_match_data(self, match_host: str, role_path: str, role_id_key: str, size: int = PREFETCH):
        my_statuses, statuses = [], []
        
        if role_path in COM:
            my_statuses = MY_STATUS_OF_COMPANY_APPLY
            statuses = STATUS_OF_COMPANY_APPLY
        elif role_path in TEACH:
            my_statuses = MY_STATUS_OF_TEACHER_APPLY
            statuses = STATUS_OF_TEACHER_APPLY
            
        match_res = await self.req.simple_get(
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

    async def logout(self, role_id: int):
        role_id_key = str(role_id)
        user = await self.__cache_check_for_auth(role_id_key)
        user_logout_status = self.__logout_status(user)

        # "LONG_TERM_TTL" for redirct notification
        await self.__cache_logout_status(role_id_key, user_logout_status)
        return (None, "successfully logged out")
    
    @staticmethod
    async def is_login(cache: ICache, visitor: BaseAuthDTO = None) -> (bool):
        if visitor is None:
            return False

        role_id_key = str(visitor.role_id)
        user: Dict = await cache.get(role_id_key)
        if user is None:
            return False

        return user.get("online", False) and \
            user.get("role", None) == visitor.role

    async def __cache_check_for_auth(self, role_id_key: str):
        user = await self.cache.get(role_id_key)
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

    async def __cache_logout_status(self, role_id_key: str, user_logout_status: Dict):
        updated = await self.cache.set(
            role_id_key, user_logout_status, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f"AuthService.__cache_logout_status fail: [cache set],\
                role_id_key:%s, user_logout_status:%s, ex:%s, cache data:%s",
                role_id_key, user_logout_status, LONG_TERM_TTL, updated)
            raise ServerException(msg="server_error")

    '''
    password
    '''
    async def send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr):
        await self.__cache_check_for_reset_password(email)
        data = await self.__req_send_reset_password_comfirm_email(auth_host, email)
        await self.__cache_token_by_reset_password(data['token'], email)
        #TEST: log
        return f'''send_email_success {data['token']}'''

    async def reset_passwrod(self, auth_host: str, verify_token: str, body: ResetPasswordVO):
        checked_email = await self.cache.get(verify_token)
        if not checked_email:
            raise UnauthorizedException(msg="invalid token") 
        if checked_email != body.register_email:
            raise UnauthorizedException(msg="invalid user")
        await self.__req_reset_password(auth_host, body)
        await self.__cache_remove_by_reset_password(verify_token, checked_email)

    
    async def __cache_check_for_reset_password(self, email: EmailStr):
        data = await self.cache.get(f'{email}:reset_pw')
        if data:
            log.error(f"AuthService.__cache_check_for_reset_password:[too many reqeusts error],\
                email:%s, cache data:%s", email, data)
            raise TooManyRequestsException(msg="frequent_requests")
    
    async def __cache_token_by_reset_password(self, verify_token: str, email: EmailStr):
        await self.cache.set(f'{email}:reset_pw', '1', REQUEST_INTERVAL_TTL)
        await self.cache.set(verify_token, email, SHORT_TERM_TTL)
        
    async def __cache_remove_by_reset_password(self, verify_token: str, email: EmailStr):
        await self.cache.delete(f'{email}:reset_pw')
        await self.cache.delete(verify_token)
        

    async def update_password(self, auth_host: str, role_id: int, body: UpdatePasswordVO):
        await self.__cache_check_for_email_validation(role_id, body.register_email)
        await self.__req_update_password(auth_host, body)

    async def __req_send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr):
        return await self.req.simple_get(
            f"{auth_host}/password/reset/email", params={'email': email}) 

    async def __cache_check_for_email_validation(self, role_id: int, register_email: EmailStr):
        role_id_key = str(role_id)
        data = await self.cache.get(role_id_key)
        if not 'email' in data or str(register_email) != data['email']:
            raise UnauthorizedException(msg='invalid email')

    async def __req_update_password(self, auth_host: str, body: UpdatePasswordVO):
        return await self.req.simple_put(
            f"{auth_host}/password/update", json=body.dict())

    async def __req_reset_password(self, auth_host: str, body: ResetPasswordVO):
        return await self.req.simple_put(
            f"{auth_host}/password/update", json=body.dict()) 
