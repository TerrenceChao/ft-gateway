import os
import time
import json
import requests
from typing import List, Dict, Any
from unicodedata import name
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from ...db.nosql import match_companies_schemas as schemas
from ..res.response import res_success, res_err
from ...common.cache import get_cache
from ...common.service_requests import get_service_requests
import logging as log


region_search_hosts = {
    # "default": os.getenv("REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/search"),
    "jp": os.getenv("JP_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/search"),
    "ge": os.getenv("EU_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/search"),
    "us": os.getenv("US_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/search"),
}

log.basicConfig(level=log.INFO)


router = APIRouter(
    prefix="/search",
    tags=["Search Resumes & Jobs"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/resumes")
def get_resumes(rid: int,
                limit: int,
                orderby: str,
                q: Any = Query(None),
                current_region: str = Header(...),
                requests=Depends(get_service_requests),
):
    current_region = current_region.lower()
    match_host = region_search_hosts[current_region]
    data, err = requests.get(
        url=f"{match_host}/resumes",
        params={
            "rid": rid,
            "limit": limit,
            "orderby": orderby,
            "q": q,
        }
    )
    
    if err:
        return res_err(msg=err)
    
    return res_success(data=data)


@router.get("/jobs")
def get_jobs(jid: int,
             limit: int,
             orderby: str,
             q: str = Query(None),
             current_region: str = Header(...),
             requests=Depends(get_service_requests),
):
    current_region = current_region.lower()
    match_host = region_search_hosts[current_region]
    data, err = requests.get(
        url=f"{match_host}/jobs",
        params={
            "jid": jid,
            "limit": limit,
            "orderby": orderby,
            "q": q,
        }
    )
    
    if err:
        return res_err(msg=err)
    
    return res_success(data=data)