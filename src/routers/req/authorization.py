import os
import time
from datetime import datetime
from typing import Callable, List, Union
import jwt as jwt_util
from fastapi import APIRouter, FastAPI, Header, Body, Request, Response
from fastapi.routing import APIRoute
from ...db.nosql import match_companies_schemas as com_schema, \
    match_teachers_schemas as teacher_schema
from ...configs.conf import JWT_SECRET, TOKEN_EXPIRE_TIME
from ...configs.exceptions import ServerException, UnauthorizedException, NotFoundException
import logging as log

log.basicConfig(level=log.INFO)


# token required in Header
def token_required(token: str = Header(...)):
    pass

def __get_secret(role_id):
    return str(role_id) # if "role_id" in data else JWT_SECRET

def gen_token(data: dict, fields: List):
    public_info = {}
    if not "role_id" in data:
        log.error(f" 'role_id' is required in data, data:{data}, fields:{fields}")
        raise ServerException(msg="internal server error")
    
    secret = __get_secret(data["role_id"])
    for field in fields:
        val = str(data[field])
        public_info[field] = val
        
    exp = datetime.now().timestamp() + TOKEN_EXPIRE_TIME
    public_info.update({ "exp": exp })
    return jwt_util.encode(payload=public_info, key=secret, algorithm="HS256")




# url_path = "//api/v1/match/teachers/6994696629320454/resumes/0"
# url_path = "//api/v1/match/teachers/"
def get_role_id(url_path: str) -> Union[int, None]:
    try:
        return int(url_path.split('/')[6])
    except Exception as e:
        log.error(f"cannot get role_id from url path, url_path:{url_path}")
        return None

def get_role(url_path: str):
    if "/companies" in url_path:
        return "company"
    
    if "/teachers" in url_path:
        return "teacher"
    
    raise NotFoundException(msg="invalid role")

def __jwt_decode(jwt, key, algorithms, msg):
    try:
        return jwt_util.decode(jwt, key, algorithms)
    except Exception as e:
        log.error(f"__jwt_decode fail, key:{key}, algorithms:{algorithms}, msg:{msg}, jwt:{jwt}, \ne:{e}")
        raise UnauthorizedException(msg=msg)

def __valid_role(data: dict, url_path: str):
    if not "role" in data:
        return False
    
    role = data["role"]
    if role == "company":
        return "/companies" in url_path
    
    if role == "teacher":
        return "/teachers" in url_path
    
    return False

def __valid_role_id(data: dict, role_id):
    if not "role_id" in data:
        return False

    return int(data["role_id"]) == int(role_id)





def verify_token_by_company_profile(request: Request,
                                    token: str = Header(...),
                                    profile: com_schema.CompanyProfile = Body(...),
                                    ):
    if not profile or not profile.cid:
        raise UnauthorizedException(msg="invalid company user, cid is required")
    
    company_id = profile.cid
    secret = __get_secret(company_id)
    data = __jwt_decode(jwt=token, key=secret, algorithms=["HS256"], msg="invalid company user")
    if not __valid_role(data, request.url.path) or \
        not __valid_role_id(data, company_id):
        raise UnauthorizedException(msg="invalid company user")


def verify_token_by_teacher_profile(request: Request,
                                    token: str = Header(...),
                                    profile: teacher_schema.TeacherProfile = Body(...),
                                    ):
    if not profile or not profile.tid:
        raise UnauthorizedException(msg="invalid teacher user, tid is required")
    
    teacher_id = profile.tid
    secret = __get_secret(teacher_id)
    data = __jwt_decode(jwt=token, key=secret, algorithms=["HS256"], msg="invalid teacher user")
    if not __valid_role(data, request.url.path) or \
        not __valid_role_id(data, teacher_id):
        raise UnauthorizedException(msg="invalid teacher user")


def verify_token(request: Request):
    url_path = request.url.path
    role_id = get_role_id(url_path)
    role = get_role(url_path)
    
    token = request.headers["token"]
    secret = __get_secret(role_id)
    data = __jwt_decode(jwt=token, key=secret, algorithms=["HS256"], msg=f"invalid {role} user")
    if not __valid_role(data, request.url.path) or \
        not __valid_role_id(data, role_id):
        raise UnauthorizedException(msg=f"invalid {role} user")




class AuthMatchRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            
            if self.__get_role_id(request):
                verify_token(request)
            
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            log.info(f"route duration: {duration}")
            log.info(f"route response headers: {response.headers}")
            # log.info(f"route response: {response}")
            return response

        return custom_route_handler
    
    def __get_role(self, request: Request):
        return get_role(request.url.path)
    
    def __get_role_id(self, request: Request):
        return get_role_id(request.url.path)
