from typing import Any, List, Dict
from ....routers.req.authorization import gen_token
from ..value_objects.auth_vo import SignupConfirmVO, LoginVO
from ...cache import ICache
from ...service_api import IServiceApi
from ....infra.utils.util import gen_confirm_code
from ....configs.conf import SHORT_TERM_TTL, LONG_TERM_TTL
from ....configs.constants import PATHS, PREFETCH
from ....configs.region_hosts import get_auth_region_host, get_match_region_host
from ....configs.exceptions import \
    ClientException, \
    UnauthorizedException, \
    NotFoundException, \
    DuplicateUserException, \
    ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class AuthService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache

    """
    get_public_key
    """

    def get_public_key(self, host: str, timestamp: int):
        slot = timestamp % 100
        pubkey, cache_err = self.cache.get(f"pubkey_{slot}")
        if cache_err:
            raise ServerException(msg="cache fail")

        if not pubkey:
            pubkey = self.__req_get_public_key(host, timestamp)
            self.cache.set(f"pubkey_{slot}", pubkey)

        return (pubkey, None)  # data, msg

    def __req_get_public_key(self, host: str, timestamp: int):
        pubkey, err = self.req.simple_get(
            f"{host}/security/pubkey", params={"ts": timestamp})
        if err:
            raise ServerException(msg="cannot get public_key")

        return pubkey

    """
    signup
    """

    def signup(self, host: str, email: str, meta: str, region: str):
        self.__cache_check_for_duplicates(email)

        confirm_code = gen_confirm_code()
        auth_res, msg = self.__req_send_confirmcode_by_email(
            host, email, confirm_code)

        if auth_res == "email_sent" and msg == "ok":
            self.__cache_confirmcode(email, confirm_code, meta)

            # TODO remove the res here('confirm_code') during production
            res = {
                "for_testing_only": confirm_code
            }
            return (res, "email_sent")  # data, msg

        else:
            self.cache.set(email, {"region": region}, SHORT_TERM_TTL)
            raise DuplicateUserException(msg="email registered")

    def __cache_check_for_duplicates(self, email: str):
        data, cache_err = self.cache.get(email)
        if cache_err:
            log.error(f"cache data:{data}, err:{cache_err}")
            raise ServerException(msg="cache fail")

        if data:
            log.error(f"cache data:{data}")
            raise DuplicateUserException(msg="registered or registering")

    def __req_send_confirmcode_by_email(self, host: str, email: str, confirm_code: str):
        auth_res, msg, err = self.req.post(f"{host}/sendcode/email", json={
            "email": email,
            "confirm_code": confirm_code,
            "sendby": "no_exist",  # email 不存在時寄送
        })

        if err:
            log.error(f"req /sendcode/email error, err:{err}")
            raise ServerException(msg=err)

        return (auth_res, msg)

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
        user, cache_err = self.cache.get(email)
        self.__verify_confirmcode(confirm_code, user, cache_err)

        # "registering": empty data, but TTL=30sec
        self.cache.set(email, {}, ex=30)
        auth_res = self.__req_signup(host,
                                     {
                                         "email": email,
                                         # "meta": "{\"region\":\"jp\",\"role\":\"teacher\",\"pass\":\"secret\"}"
                                         "meta": user["meta"],
                                         "pubkey": body.pubkey,
                                     })

        role_id_key = str(auth_res["role_id"])
        auth_res = self.__apply_token(auth_res)
        updated, cache_err = self.cache.set(role_id_key, auth_res, ex=LONG_TERM_TTL)
        if not updated or cache_err:
            raise ServerException(msg="cache fail")
        else:
            return (auth_res, None)  # data, msg

    def __verify_confirmcode(self, confirm_code: str, user: Any, cache_err: str):
        log.info("type:%s, user:%s" % (type(user), user))
        if cache_err:
            raise ServerException(msg="cache fail")

        if not user or not "confirm_code" in user:
            raise NotFoundException(msg="no signup data")

        if user == {}:
            raise DuplicateUserException(msg="registering")

        if confirm_code != str(user["confirm_code"]):
            raise ClientException(msg="wrong confirm_code")

    def __req_signup(self, host: str, payload: Dict):
        res, err = self.req.simple_post(f"{host}/signup", json=payload)
        if err:
            raise ServerException(msg="signup fail")

        return res

    def __apply_token(self, res: Dict):
        # gen jwt token
        token = gen_token(res, ["region", "role_id", "role"])
        res.update({"token": token})
        return res

    """
    login
    """

    def login(self, auth_host: str, match_host: str, current_region: str, body: LoginVO):
        # request login & auth data
        body.current_region = current_region
        auth_res, msg = self.__req_login(auth_host, body)

        # found in S3, and region != "current_region"(在 meta, 解密後才會知道)(找錯地方)
        # S3 有記錄但該地區的 auth-service 沒記錄，auth 從 S3 找 region 後回傳
        if msg == "wrong_region":
            log.warn("WRONG REGION: \n \
                    has record in S3, but no record in DB of current region, ready to request user record from register region")
            region = auth_res["region"]  # 換其他 region 再請求一次
            auth_host = get_auth_region_host(region)
            match_host = get_match_region_host(region)
            auth_res, msg = self.__req_login(auth_host, body)

        # cache auth data
        role_id_key = str(auth_res["role_id"])
        auth_res = self.__apply_token(auth_res)
        auth_res.update({
            "current_region": current_region,
            "socketid": "it's socketid",
            "online": True,
        })
        self.__cache_auth_res(role_id_key, auth_res)

        # request match data
        role_path = PATHS[auth_res["role"]]
        size = body.prefetch or PREFETCH
        match_res = self.__req_match_data(
            match_host, role_path, role_id_key, size)

        return ({
            "auth": auth_res,
            "match": match_res,
        }, None)  # data, msg

    def __req_login(self, auth_host: str, body: LoginVO):
        auth_res, msg, err = self.req.post(
            f"{auth_host}/login", json=body.dict())

        # found in DB
        if msg == "error_password":
            raise ClientException(msg="error_password")

        # not found in DB and S3
        if msg == "not_registered":
            raise NotFoundException(msg="user not found")  # 沒註冊過

        # found in S3, and region == "current_region"(在 meta, 解密後才會知道)(S3記錄:註冊在該auth_service卻找不到)
        if msg == "register_fail":
            raise ServerException(msg="register fail")  # {log_level:嚴重問題}

        if err:
            raise ServerException(msg=err)

        return (auth_res, msg)

    def __cache_auth_res(self, role_id_key: str, auth_res: Dict):
        updated, cache_err = self.cache.set(role_id_key, auth_res, ex=LONG_TERM_TTL)
        if not updated or cache_err:
            raise ServerException(msg="cache fail")

    def __req_match_data(self, match_host: str, role_path: str, role_id_key: str, size: int):
        match_res, err = self.req.simple_get(
            f"{match_host}/{role_path}/{role_id_key}/matchdata?size={size}")
        if err:
            log.error(f"req match data fail: {err}")
            return None

        return match_res

    """
    logout
    """

    def logout(self, role_id: int, token: str):
        role_id_key = str(role_id)
        user = self.__cache_check_for_auth(role_id_key, token)
        if not user or not "token" in user:
            return (None, "logged out")

        user_logout_status = self.__logout_status(user)

        # "LONG_TERM_TTL" for redirct notification
        self.__cache_logout_status(role_id_key, user_logout_status)
        return (None, "successfully logged out")

    def __cache_check_for_auth(self, role_id_key: str, token: str):
        user, cache_err = self.cache.get(role_id_key)
        if cache_err:
            raise ServerException(msg="cache fail")

        if user["token"] != token:
            raise UnauthorizedException(msg="access denied")

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
        updated, cache_err = self.cache.set(role_id_key, user_logout_status, ex=LONG_TERM_TTL)
        if not updated or cache_err:
            raise ServerException(msg="cache fail")
