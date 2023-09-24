from typing import List, Dict, Any
from unicodedata import name
from fastapi import APIRouter, \
    Request, Depends, \
    Header, Path, Query, Body, Form, \
    HTTPException
from ..res.response import res_success, res_err
from ...infra.db.nosql import match_companies_schemas as schemas
from ...apps.service_api_dapter import ServiceApiAdapter, get_service_requests
from ...configs.region_hosts import get_search_region_host
import logging as log

log.basicConfig(filemode='w', level=log.INFO)

def get_search_host(region: str = Header(...)):
    return get_search_region_host(region=region)



router = APIRouter(
    prefix="/search",
    tags=["Search Jobs & Resumes"],
    responses={404: {"description": "Not found"}},
)


@router.get("/resumes")
def get_resumes(limit: int,
                orderby: str,
                q: Any = Query(None),
                search_host=Depends(get_search_host),
                requests=Depends(get_service_requests),
):
    data, err = requests.get(f"{search_host}/resumes")
    if err:
        return res_err(msg=err)
    
    return res_success(data=data)


@router.get("/resumes/{rid}")
def get_resume_by_id(rid: int,
                    search_host=Depends(get_search_host),
                    requests=Depends(get_service_requests),
):
    data, err = requests.get(f"{search_host}/resumes/{rid}")
    if err:
        return res_err(msg=err)
    
    return res_success(data=data)


@router.get("/jobs")
def get_jobs(limit: int,
            orderby: str,
            q: Any = Query(None),
            search_host=Depends(get_search_host),
            requests=Depends(get_service_requests),
):
    data, err = requests.get(f"{search_host}/jobs")
    if err:
        return res_err(msg=err)
    
    return res_success(data=data)


@router.get("/jobs/{jid}")
def get_job_by_id(jid: int,
                search_host=Depends(get_search_host),
                requests=Depends(get_service_requests),
):
    data, err = requests.get(f"{search_host}/jobs/{jid}")
    if err:
        return res_err(msg=err)
    
    return res_success(data=data)
