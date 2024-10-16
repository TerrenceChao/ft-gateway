from typing import List
from unicodedata import name
from fastapi import APIRouter, \
    Depends, Header, Query
from ..req.search_validation import *
from ..res.response import *
from ...apps.resources.adapters import service_client, gw_cache
from ...configs.region_hosts import \
    get_search_region_host, get_match_region_host
from ...configs.constants import *
from ...domains.search.value_objects import \
    c_value_objects as search_c, t_value_objects as search_t, \
    public_value_objects as search_public
from ...domains.match.company.value_objects import c_value_objects as match_c
from ...domains.match.teacher.value_objects import t_value_objects as match_t
from ...domains.search.services.search_service import SearchService
from ...domains.match.star_tracker_service import StarTrackerService
from ...domains.user.services.auth_service import AuthService
from ...domains.user.value_objects.auth_vo import BaseAuthDTO
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


router = APIRouter(
    prefix="/search",
    tags=["Search Jobs & Resumes"],
    responses={404: {"description": "Not found"}},
)


async def get_search_host(current_region: str = Header(...)):
    return get_search_region_host(region=current_region)


async def get_match_host(region: str = Header(...)):
    return get_match_region_host(region=region)


SEARCH = 'search'
_search_service = SearchService(
    service_client,
    gw_cache,
)
_star_tracker_service = StarTrackerService(
    service_client,
    gw_cache,
)


@router.get("/resumes",
            responses=idempotent_response(f'{SEARCH}.get_resumes', search_t.SearchResumeListVO))
async def get_resumes(
    size: int = Query(10, gt=0, le=100),
    sort_by: SortField = Query(SortField.UPDATED_AT),
    sort_dirction: SortDirection = Query(SortDirection.DESC),
    next: str = Query(None),
    patterns: List[str] = Query([]),
    tags: List[str] = Query([]),
    visitor: BaseAuthDTO = Depends(search_list_check_visitor),
    search_host=Depends(get_search_host),
    match_host=Depends(get_match_host),
):
    query = search_t.SearchResumeListQueryDTO(
        size=size,
        sort_by=sort_by,
        sort_dirction=sort_dirction,
        search_after=next,
        patterns=patterns,
        tags=tags,
    )
    data = await _search_service.get_resumes(search_host, query)
    if AuthService.is_login(gw_cache, visitor):
        data.items = await _star_tracker_service.all_marks(
            match_host,
            visitor,
            data.items,
        )
    return res_success(data=data)


@router.get("/resumes/{region}/{tid}/{rid}",
            responses=idempotent_response(f'{SEARCH}.get_resume_by_id', match_t.TeacherProfileAndResumeVO))
async def get_resume_by_id(
    tid: int,
    rid: int,
    match_host=Depends(get_match_host),
):
    (data, msg) = await _search_service.get_resume_by_id(match_host, tid, rid)
    return res_success(data=data, msg=msg)


@router.get('/resumes-info/tags',
            responses=idempotent_response(f'{SEARCH}.get_resume_tags', search_public.ResumeTagsVO))
async def get_resume_tags(
    search_host=Depends(get_search_host),
):
    data = await _search_service.get_resume_tags(search_host)
    return res_success(data=data)


@router.get("/jobs",
            responses=idempotent_response(f'{SEARCH}.get_jobs', search_c.SearchJobListVO))
async def get_jobs(
    size: int = Query(10, gt=0, le=100),
    sort_by: SortField = Query(SortField.UPDATED_AT),
    sort_dirction: SortDirection = Query(SortDirection.DESC),
    next: str = Query(None),
    patterns: List[str] = Query([]),
    continent_code: str = Query(None),
    country_code: str = Query(None),
    visitor: BaseAuthDTO = Depends(search_list_check_visitor),
    search_host=Depends(get_search_host),
    match_host=Depends(get_match_host),
):
    query = search_c.SearchJobListQueryDTO(
        size=size,
        sort_by=sort_by,
        sort_dirction=sort_dirction,
        search_after=next,
        patterns=patterns,
        continent_code=continent_code,
        country_code=country_code,
    )
    data = await _search_service.get_jobs(search_host, query)
    if AuthService.is_login(gw_cache, visitor):
        data.items = await _star_tracker_service.all_marks(
            match_host,
            visitor,
            data.items,
        )
    return res_success(data=data)


@router.get("/jobs/{region}/{cid}/{jid}",
            responses=idempotent_response(f'{SEARCH}.get_job_by_id', match_c.CompanyProfileAndJobVO))
async def get_job_by_id(
    cid: int,
    jid: int,
    match_host=Depends(get_match_host),
):
    (data, msg) = await _search_service.get_job_by_id(match_host, cid, jid)
    return res_success(data=data, msg=msg)


@router.get('/jobs-info/continents',
            responses=idempotent_response(f'{SEARCH}.get_continents', search_public.ContinentListVO))
async def get_continents(search_host=Depends(get_search_host)):
    data = await _search_service.get_continents(search_host)
    return res_success(data=data)


# TODO: this route rule(get_all_continents_and_countries) is same as 'get_countries',
# so it has to be put before 'get_countries'
@router.get('/jobs-info/continents/all/countries',
            responses=idempotent_response(f'{SEARCH}.get_all_continents_and_countries', List[search_public.CountryListVO]))
async def get_all_continents_and_countries(search_host=Depends(get_search_host)):
    data = await _search_service.get_all_continents_and_countries(search_host)
    return res_success(data=data)


@router.get('/jobs-info/continents/{continent_code}/countries',
            responses=idempotent_response(f'{SEARCH}.get_countries', List[search_public.CountryListVO]))
async def get_countries(
    continent_code: str,
    search_host=Depends(get_search_host),
):
    data = await _search_service.get_countries(
        search_host,
        continent_code,
    )
    return res_success(data=data)
