from domains.cache import ICache
from domains.service_api import IServiceApi
from src.domains.cache import ICache
from src.domains.service_api import IServiceApi
from src.domains.service_api import IServiceApi
from src.domains.cache import ICache
from src.configs.exceptions import *
from src.configs.constants import PATHS
from src.configs.region_hosts import get_auth_region_host, get_match_region_host
import logging as log
import json

from src.domains.user.services.auth_service import AuthService


class ISSOAuthService(AuthService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)

    def dialog(self, auth_host: str, role: str):
        return self.__req_get_dialog(self, auth_host, role)

    def login(self, auth_host: str, match_host: str, code: str, state: str):
        (auth_res, region) = self.__req_login_or_register_region(auth_host, match_host, code, state)
        if auth_res is None:
            auth_host = get_auth_region_host(region)
            match_host = get_match_region_host(region)
            auth_res = self.__req_get_login(auth_host, match_host, code, state)

        state_d = json.loads(state)
        if not (current_region := state_d.get('region', '')):
            raise ServerException(msg="no region") 

        # cache auth data
        role_id_key = str(auth_res["role_id"])
        auth_res.update({
            "current_region": current_region,
            "socketid": "it's socketid",
        })
        self.cache_auth_res(role_id_key, auth_res)
        auth_res = self.apply_token(auth_res)

        # request match data
        role_path = PATHS[auth_res["role"]]
        match_res = self.__req_match_data(
            match_host,
            role_path,
            role_id_key,
        )

        return {
            "auth": auth_res,
            "match": match_res,
        }


    def __req_get_dialog(self, auth_host: str, role: str):
        pass

    def __req_get_login(self, auth_host: str, code: str, state: str):
        pass

        
    def __req_login_or_register_region(self, auth_host: str, match_host: str, code: str, state: str):
        register_region = None
        auth_res = None
        try:
            auth_res = self.__req_get_login(auth_host, code, state)
            return (auth_res, None)
            
        except ForbiddenException as exp_payload:
            # found in S3, and region != "current_region"(在 meta, 解密後才會知道)(找錯地方)
            # S3 有記錄但該地區的 auth-service 沒記錄，auth 從 S3 找 region 後回傳
            log.error(f"AuthService.login fail: [WRONG REGION: there is the user record in S3, \
                but no record in the DB of current region, it's ready to request the user record from register region], \
                auth_host:%s, match_host:%s, code:%s, state:%s register_region:%s, auth_res:%s, exp_payload:%s", 
                auth_host, match_host, code, state, register_region, auth_res, exp_payload.msg)
                
            try:
                email_info = exp_payload.data
                register_region = email_info["region"]  # 換其他 region 再請求一次
                return (None, register_region)
                
            except Exception as format_err:
                log.error(f"AuthService.login fail: [exp_payload format_err], \
                    auth_host:%s, match_host:%s, code:%s, state:%s, auth_res:%s, exp_payload:%s, format_err:%s", 
                    auth_host, match_host, code, state, auth_res, exp_payload, format_err.__str__())
                raise ServerException(msg="format_err")
            
        except Exception as e:
            log.error(f"AuthService.login fail: [unknow_error], \
                auth_host:%s, match_host:%s, code:%s, state:%s register_region:%s, auth_res:%s, err:%s", 
                auth_host, match_host, code, state, register_region, auth_res, e.__str__())
            raise_http_exception(e, 'unknow_error')

class FBAuthService(ISSOAuthService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)

    def __req_get_dialog(self, auth_host: str, role: str):
        return self.req.simple_get(
            f"{auth_host}/fb/dialog", params={'role': role})
    
    def __req_get_login(self, auth_host: str, code: str, state: str):
        return self.req.simple_get(
            f"{auth_host}/fb/login", params={'code': code, 'state': state}
        )

class GoogleAuthService(ISSOAuthService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)

    def __req_get_dialog(self, auth_host: str, role: str):
        return self.req.simple_get(
            f"{auth_host}/google/dialog", params={'role': role})
    
    def __req_get_login(self, auth_host: str, code: str, state: str):
        return self.req.simple_get(
            f"{auth_host}/google/login", params={'code': code, 'state': state}
        )
