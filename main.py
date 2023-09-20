import os
import json
from sys import prefix
from mangum import Mangum
from typing import Optional, List, Dict
from fastapi import FastAPI, Request, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException, \
    Depends, \
    APIRouter
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from src.routers.v1 import auth, \
    match_companies, match_teachers, \
    search, media

from src.routers.v2 import auth as authv2
from src.routers.res.response import res_err
from src.configs import exceptions
from src.configs.region_hosts import RegionException




STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'
app = FastAPI(title="ForeignTeacher: Gateway", root_path=root_path)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BusinessEception(Exception):
    def __init__(self, term: str):
        self.term = term

@app.exception_handler(BusinessEception)
async def business_exception_handler(request: Request, exc: BusinessEception):
    return JSONResponse(
        status_code=418,
        content={
            "code": 1,
            "msg": f"Oops! {exc.term} is a wrong phrase. Guess again?"
        }
    )


@app.exception_handler(RegionException)
async def region_exception_handler(request: Request, exc: RegionException):
    return JSONResponse(
        status_code=exc.status_code,
        content=res_err(msg=exc.msg)
    )


exceptions.include_app(app)




router_v1 = APIRouter(prefix="/api/v1")
# TODO: other routers
router_v1.include_router(auth.router)
router_v1.include_router(match_companies.router)
router_v1.include_router(match_teachers.router)
router_v1.include_router(search.router)
router_v1.include_router(media.router)


router_v2 = APIRouter(prefix="/api/v2")
router_v2.include_router(authv2.router)




app.include_router(router_v1)
app.include_router(router_v2)


@app.get("/gateway/{term}")
async def info(term: str):
    if term != "yolo":
        raise BusinessEception(term=term)
    return {"mention": "You only live once"}


# Mangum Handler, this is so important
handler = Mangum(app)
