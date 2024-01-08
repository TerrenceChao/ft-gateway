import requests
from typing import List, Dict, Any
from unicodedata import name
from fastapi import APIRouter, \
    Request, Depends, \
    Header, Path, Query, Body, Form
from ..res.response import *
from ...apps.service_api_dapter import \
    ServiceApiAdapter, get_service_requests
from ...configs.region_hosts import \
    get_search_region_host, get_match_region_host
from ...configs.constants import *
from ...domains.search.value_objects import \
    c_value_objects as search_c, t_value_objects as search_t
from ...domains.match.company.value_objects import c_value_objects as match_c
from ...domains.match.teacher.value_objects import t_value_objects as match_t
from ...domains.search.services.search_service import SearchService
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix="/search",
    tags=["Search Jobs & Resumes"],
    responses={404: {"description": "Not found"}},
)


def get_search_host(current_region: str = Header(...)):
    return get_search_region_host(region=current_region)


def get_match_host(region: str = Path(...)):
    return get_match_region_host(region=region)


SEARCH = 'search'
_search_service = SearchService(
    ServiceApiAdapter(requests)
)


@router.get("/resumes",
            responses=idempotent_response(f'{SEARCH}.get_resumes', search_t.ResumeListVO))
def get_resumes(
    size: int = Query(10, gt=0, le=100),
    sort_by: SortField = Query(SortField.UPDATED_AT),
    sort_dirction: SortDirection = Query(SortDirection.DESC),
    search_after: str = Query(None),
    search_host=Depends(get_search_host),
):
    query = search_t.SearchResumeListVO(
        size=size,
        sort_by=sort_by,
        sort_dirction=sort_dirction,
        search_after=search_after,
    )
    data = _search_service.get_resumes(search_host, query)
    return res_success(data=data)


@router.get("/resumes/{region}/{tid}/{rid}",
            responses=idempotent_response(f'{SEARCH}.get_resume_by_id', match_t.TeacherProfileAndResumeVO))
def get_resume_by_id(
    tid: int,
    rid: int,
    match_host=Depends(get_match_host),
):
    data = _search_service.get_resume_by_id(match_host, tid, rid)
    return res_success(data=data)


@router.get("/jobs",
            responses=idempotent_response(f'{SEARCH}.get_jobs', search_c.JobListVO))
def get_jobs(
    size: int = Query(10, gt=0, le=100),
    sort_by: SortField = Query(SortField.UPDATED_AT),
    sort_dirction: SortDirection = Query(SortDirection.DESC),
    search_after: str = Query(None),
    search_host=Depends(get_search_host),
):
    query = search_c.SearchJobListVO(
        size=size,
        sort_by=sort_by,
        sort_dirction=sort_dirction,
        search_after=search_after,
    )
    data = _search_service.get_jobs(search_host, query)
    return res_success(data=data)


@router.get("/jobs/{region}/{cid}/{jid}",
            responses=idempotent_response(f'{SEARCH}.get_job_by_id', match_c.CompanyProfileAndJobVO))
def get_job_by_id(
    cid: int,
    jid: int,
    match_host=Depends(get_match_host),
):
    data = _search_service.get_job_by_id(match_host, cid, jid)
    return res_success(data=data)
