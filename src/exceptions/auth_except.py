from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from ..routers.res.response import res_err
import logging as log


log.basicConfig(level=log.ERROR)

class ErrorLogger:
    def __init__(self, msg: str):
        log.error(msg)
        

class ClientException(HTTPException, ErrorLogger):
    def __init__(self, msg: str):
        self.msg = msg
        self.status_code = status.HTTP_400_BAD_REQUEST
        
class UnauthorizedException(HTTPException, ErrorLogger):
    def __init__(self, msg: str):
        self.msg = msg
        self.status_code = status.HTTP_401_UNAUTHORIZED

class NotFoundException(HTTPException, ErrorLogger):
    def __init__(self, msg: str):
        self.msg = msg
        self.status_code = status.HTTP_404_NOT_FOUND

class DuplicateUserException(HTTPException, ErrorLogger):
    def __init__(self, msg: str):
        self.msg = msg
        self.status_code = status.HTTP_406_NOT_ACCEPTABLE
        
class ServerException(HTTPException, ErrorLogger):
    def __init__(self, msg: str):
        self.msg = msg
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


def __client_exception_handler(request: Request, exc: ClientException):
    return JSONResponse(status_code=exc.status_code, content=res_err(msg=exc.msg))

def __unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(status_code=exc.status_code, content=res_err(msg=exc.msg))

def __not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=exc.status_code, content=res_err(msg=exc.msg))

def __duplicate_user_exception_handler(request: Request, exc: DuplicateUserException):
    return JSONResponse(status_code=exc.status_code, content=res_err(msg=exc.msg))

def __server_exception_handler(request: Request, exc: ServerException):
    return JSONResponse(status_code=exc.status_code, content=res_err(msg="unknow server error"))




def include_app(app: FastAPI):
    app.add_exception_handler(ClientException, __client_exception_handler)
    app.add_exception_handler(UnauthorizedException, __unauthorized_exception_handler)
    app.add_exception_handler(NotFoundException, __not_found_exception_handler)
    app.add_exception_handler(DuplicateUserException, __duplicate_user_exception_handler)
    app.add_exception_handler(ServerException, __server_exception_handler)
