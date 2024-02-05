import os
import time
from datetime import datetime
from typing import Callable, List, Union, Dict
import jwt as jwt_util
from fastapi import APIRouter, FastAPI, Header, Path, Query, Body, Request, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.routing import APIRoute
from ...domains.user.value_objects.auth_vo import \
    gen_expired_timestamp, UpdateTokenDTO
from ...infra.db.nosql import match_companies_schemas as com_schema, \
    match_teachers_schemas as teacher_schema
from ...configs.conf import JWT_SECRET, JWT_ALGORITHM, TOKEN_EXPIRE_TIME, REFRESH_TOKEN_TIME_WINDOW
from ...configs.exceptions import *
import logging as log

log.basicConfig(level=log.INFO)

auth_scheme = HTTPBearer()


# token required in Header
def token_required(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    pass

def parse_token(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    if not token:
        log.error(f"parse_token fail: ['token' is required in credentials], credentials:{credentials}")
        raise UnauthorizedException(msg="Authorization failed")
    
    return token

async def parse_token_from_request(request: Request):
    credentials: HTTPAuthorizationCredentials = await auth_scheme.__call__(request)
    if not credentials:
        raise UnauthorizedException(msg="Authorization header missing")
    
    return parse_token(credentials)


def __get_secret(role_id):
    return f"secret{str(role_id)[::-1]}" # if role_id != None else JWT_SECRET


def gen_token(data: dict, fields: List, expired_timestamp: float = None) -> (str):
    public_info = {}
    if not "role_id" in data:
        log.error(f"gen_token fail: ['role_id' is required in data], data:{data}, fields:{fields}")
        raise ServerException(msg="internal server error")
    
    secret = __get_secret(data["role_id"])
    for field in fields:
        val = str(data[field])
        public_info[field] = val

    if expired_timestamp is None:
        exp = gen_expired_timestamp()
    else:
        exp = expired_timestamp

    public_info.update({ "exp": exp })
    return jwt_util.encode(payload=public_info, key=secret, algorithm=JWT_ALGORITHM)


def valid_time_window() -> (float):
    return gen_expired_timestamp() + REFRESH_TOKEN_TIME_WINDOW


def grant_new_token_check(
    body: UpdateTokenDTO = Body(...),
    current_region: str = Header(...),
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    try:
        token = credentials.credentials
        secret = __get_secret(body.role_id)
        # Throw ExpiredSignatureError if token is expired. Don't raise Exception, let auth-service handle it.
        data = jwt_util.decode(token, secret, [JWT_ALGORITHM])
        # FIXME: 2024/02/05 disable 'return body'
        return body

        # FIXME: 2024/02/05 enable the following code
        # # token is expired TOO LONG, more then exceptable time window
        # if data['exp'] > valid_time_window():
        #     raise UnauthorizedException(msg="token is expired, need to login again")

        # # toekn passed, it means the data is correct and not expired, need throw client exception
        # raise ClientException(msg="token is not expired yet, no need to refresh it")

    except jwt_util.ExpiredSignatureError:
        log.warn(f"As expectation, token has expired, \
            body:{body}, current_region:{current_region}, token:{token}")
        # Throw ExpiredSignatureError if token is expired. Don't raise Exception, let auth-service handle it.
        # TODO: CANNOT check the role & role_id, send request to auth-service then check role_id & refresh_token
        return body

    except ClientException as e:
        raise ClientException(msg=e.msg)

    except Exception as e:
        log.error(f"invalid token, body:{body}, current_region:{current_region}, token:{token}, e:{e}")
        raise UnauthorizedException(msg=e.msg if isinstance(e, UnauthorizedException) else f"invalid user")


# url_path = "//api/v1/match/teachers/6994696629320454/resumes/0"
# url_path = "//api/v1/match/teachers/"
def get_role_id(url_path: str) -> (int):
    try:
        return int(url_path.split('/')[6])
    except Exception as e:
        log.error(f"cannot get role_id from url path, url_path:{url_path}, err:{e}")
        raise NotFoundException(msg="'role_id' is not found in url path")

def get_role(url_path: str):
    if "/companies" in url_path or "/company" in url_path:
        return "company"
    
    if "/teachers" in url_path or "/teacher" in url_path:
        return "teacher"
    
    raise NotFoundException(msg="'role' is not found in url path")

def __jwt_decode(jwt, key, msg):
    try:
        algorithms = [JWT_ALGORITHM]
        return jwt_util.decode(jwt, key, algorithms)
    except Exception as e:
        log.error(f"__jwt_decode fail, key:{key}, algorithms:{algorithms}, msg:{msg}, jwt:{jwt}, \ne:{e}")
        raise UnauthorizedException(msg=msg)

def __valid_role(data: dict, url_path: str):
    if not "role" in data:
        return False
    
    role = data["role"]
    if role == "company":
        return "/companies" in url_path or "/company" in url_path
    
    if role == "teacher":
        return "/teachers" in url_path or "/teacher" in url_path
    
    return False

def __valid_role_id(data: dict, role_id):
    if not "role_id" in data:
        return False

    return int(data["role_id"]) == int(role_id)



def __verify_token_in_match(role_id: int, url_path: str, credentials: HTTPAuthorizationCredentials, err_msg: str):
    secret = __get_secret(role_id)
    token = parse_token(credentials)
    data = __jwt_decode(jwt=token, key=secret, msg=err_msg)
    if not __valid_role(data, url_path) or \
        not __valid_role_id(data, role_id):
        raise UnauthorizedException(msg=err_msg)


def verify_token_by_company_profile(request: Request,
                                    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
                                    profile: com_schema.CompanyProfile = Body(...),
                                    ):
    if not profile or not profile.cid:
        raise UnauthorizedException(msg="invalid company user, cid is required")
    
    __verify_token_in_match(profile.cid, request.url.path, credentials, "invalid company user")


def verify_token_by_teacher_profile(request: Request,
                                    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
                                    profile: teacher_schema.TeacherProfile = Body(...),
                                    ):
    if not profile or not profile.tid:
        raise UnauthorizedException(msg="invalid teacher user, tid is required")
    
    __verify_token_in_match(profile.tid, request.url.path, credentials, "invalid teacher user")



def __verify_token_in_auth(role_id: int, credentials: HTTPAuthorizationCredentials, err_msg: str):
    secret = __get_secret(role_id)
    token = parse_token(credentials)
    data = __jwt_decode(jwt=token, key=secret, msg=err_msg)
    if not __valid_role_id(data, role_id):
        raise UnauthorizedException(msg=err_msg)


def verify_token_by_logout(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
                           role_id: int = Body(..., embed=True),
                           ):
    __verify_token_in_auth(role_id, credentials, "invalid user")
    
    
def verify_token_by_update_password(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
                                    role_id: int = Path(...),
                                    ):
    __verify_token_in_auth(role_id, credentials, "access denied")


# payment
def __verify_token_in_payment(role_id: int, credentials: HTTPAuthorizationCredentials, err_msg: str):
    secret = __get_secret(role_id)
    token = parse_token(credentials)
    data = __jwt_decode(jwt=token, key=secret, msg=err_msg)
    
    if data.get('role', None) != 'company':
        raise UnauthorizedException(msg='payments are only allowed for company role')
    
    if not __valid_role_id(data, role_id):
        raise UnauthorizedException(msg=err_msg)
    
def verify_token_by_subscribe_status(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
                                    role_id: int = Query(...),
                                    ):
    __verify_token_in_payment(role_id, credentials, 'unauthorized user')
    
def verify_token_by_payment_operation(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
                                      body: Dict = Body(...),
                                      ):
    if not 'role_id' in body:
        raise UnauthorizedException(msg='unauthorized payment user') 
    
    __verify_token_in_payment(body.get('role_id'), credentials, 'unauthorized payment user')


async def verify_token(request: Request):
    url_path = request.url.path
    role = get_role(url_path)
    role_id = get_role_id(url_path)
    
    token = await parse_token_from_request(request)
    secret = __get_secret(role_id)
    data = __jwt_decode(jwt=token, key=secret, msg=f"invalid {role} user")
    if not __valid_role(data, url_path) or \
        not __valid_role_id(data, role_id):
        raise UnauthorizedException(msg=f"invalid {role} user")




class AuthRoute(APIRoute):
    def get_route_handler(self) -> (Callable):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            
            await verify_token(request)
            
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            log.info(f"route duration: {duration}")
            log.info(f"route response headers: {response.headers}")
            # log.info(f"route response: {response}")
            return response

        return custom_route_handler

