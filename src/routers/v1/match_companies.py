import os
import time
import json
import requests
from typing import List, Dict, Any
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from ...exceptions.match_except import ClientException, \
    NotFoundException, \
    ServerException
from ...db.nosql import match_companies_schemas as schemas
from ..req.authorization import AuthMatchRoute, token_required, verify_token_by_company_profile
from ..res.response import res_success
from ...common.service_requests import get_service_requests
from ...common.region_hosts import get_match_region_host
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix="/match/companies",
    tags=["Match Companies"],
    dependencies=[Depends(token_required)],
    route_class=AuthMatchRoute,
    responses={404: {"description": "Not found"}},
)


def get_match_host(current_region: str = Header(...)):
    return get_match_region_host(region=current_region)


"""[此 API 在一開始註冊時會用到]
Returns:
    [Company]: [description]
"""
@router.post("/", status_code=201)
def create_profile(profile: schemas.CompanyProfile,
                   match_host=Depends(get_match_host),
                   requests=Depends(get_service_requests),
                   # cache=Depends(get_cache),
                   verify=Depends(verify_token_by_company_profile),
                   ):
    data, err = requests.post(url=f"{match_host}/companies/",
                             json=profile.dict())
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


# TODO: 未來如果允許使用多個 jobs, 須考慮 idempotent
@router.post("/{company_id}/jobs", status_code=201)
def create_job(
    company_id: int,
    profile: schemas.CompanyProfile = Body(None, embed=True),  # Nullable
    job: schemas.Job = Body(..., embed=True),
    match_host=Depends(get_match_host),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    data, err = requests.post(
        url=f"{match_host}/companies/{company_id}/jobs",
        json={
            "profile": None if profile == None else profile.dict(),
            "job": job.dict()
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


@router.get("/{company_id}/jobs/{job_id}")
def get_job(company_id: int, job_id: int,
            match_host=Depends(get_match_host),
            requests=Depends(get_service_requests),
            # cache=Depends(get_cache)
            ):
    data, err = requests.get(
        url=f"{match_host}/companies/{company_id}/jobs/{job_id}")
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


# # TODO: deprecated
# @router.get("/{company_id}/jobs")
# def get_jobs(company_id: int):
#   return res


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.put("/{company_id}/jobs/{job_id}")
def update_job(
    company_id: int,
    job_id: int,
    profile: schemas.CompanyProfile = Body(None, embed=True),  # Nullable
    job: schemas.Job = Body(None, embed=True),  # Nullable,
    match_host=Depends(get_match_host),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    if profile == None and job == None:
        raise ClientException(msg="at least one of the profile or job is required")

    data, err = requests.put(
        url=f"{match_host}/companies/{company_id}/jobs/{job_id}",
        json={
            "profile": profile.dict(),
            "job": job.dict()
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


"""[可見度]
TODO: 未來如果允許使用多個 jobs:
A. 可以將 jobs 設定為一主多備 (只採用一個，其他為備用)
  enable=True:  job.id=jid 設為 True, 其它設為 False
  enable=False: 所有 job 設為 False
  
B. 可同時使用多個 jobs. 針對不同 teacher/resume 配對不同 job
"""
@router.put("/{company_id}/jobs/{job_id}/enable/{enable}")
def enable_job(company_id: int, job_id: int, enable: bool,
               match_host=Depends(get_match_host),
               requests=Depends(get_service_requests),
               # cache=Depends(get_cache)
               ):
    data, err = requests.put(
        url=f"{match_host}/companies/{company_id}/jobs/{job_id}/enable/{enable}")
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


# # TODO: ?? 有需要批次更新 resumes 再實現
# @router.put("/{company_id}/resumes/follow")
# def upsert_follow_resumes(company_id: int, resumesInfo: List[schemas.FollowResume] = Body(...),
#                           match_host=Depends(get_match_host),
#                           requests=Depends(get_service_requests),
#                           # cache=Depends(get_cache)
#                           ):
#     # TODO: for remote batch update; resume's'Info 是多個 FollowResume
#     pass


@router.get("/{company_id}/jobs/brief")
def get_brief_jobs(company_id: int, job_id: int = Query(None), size: int = Query(None),
                   match_host=Depends(get_match_host),
                   requests=Depends(get_service_requests),
                   # cache=Depends(get_cache)
                   ):
    data, err = requests.get(
        url=f"{match_host}/companies/{company_id}/jobs/brief",
        params={
            "job_id": int(job_id),
            "size": int(size)
        })
    log.info(data)
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)





def resume_request_body(register_region: str = Header(None), current_region: str = Header(...), resume: Dict = Body(...), jobInfo: Dict = Body(...)):
    return {
        "register_region": register_region,
        "current_region": current_region,
        "resume": resume,
        "jobInfo": jobInfo
    }


# TODO: resume_info: Dict >> resume_info 是 "ContactResume".resume_info (Dict/JSON, 是 Contact!!)
@router.put("/{company_id}/jobs/{job_id}/resumes/{resume_id}/apply")
def apply_resume(company_id: int, job_id: int, resume_id: int, body=Depends(resume_request_body),
                 requests=Depends(get_service_requests),
                 # cache=Depends(get_cache)
                 ):
    match_host = get_match_region_host(region=body["current_region"])
    contact_resume, err = requests.put(
        url=f"{match_host}/companies/{company_id}/jobs/{job_id}/resumes/{resume_id}/apply",
        json={
            "resume": body["resume"],
            "jobInfo": body["jobInfo"]
        },
        headers={
            "register_region": body["register_region"],
            "current_region": body["current_region"]
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=contact_resume)


# TODO: resume_info: Dict >> resume_info 是 "ContactResume".resume_info (Dict/JSON, 是 Contact!!)
@router.put("/{company_id}/jobs/{job_id}/resumes/{resume_id}/reply")
def reply_resume(company_id: int, job_id: int, resume_id: int, body=Depends(resume_request_body),
                 requests=Depends(get_service_requests),
                 # cache=Depends(get_cache)
                 ):
    match_host = get_match_region_host(region=body["current_region"])
    contact_resume, err = requests.put(
        url=f"{match_host}/companies/{company_id}/jobs/{job_id}/resumes/{resume_id}/reply",
        json={
            "resume": body["resume"],
            "jobInfo": body["jobInfo"]
        },
        headers={
            "register_region": body["register_region"],
            "current_region": body["current_region"]
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=contact_resume)


# # TODO: remote event bus
# # TODO: resume_info: Dict >> resume_info 是 "ContactResume".resume_info (Dict/JSON, 是 Contact!!)
# @router.put("/{company_id}/jobs/{job_id}/resumes/{resume_id}/apply/remote")
# def remote_apply_resume(company_id: int, job_id: int, resume_id: int, body=Depends(resume_request_body),
#                         requests=Depends(get_service_requests),
#                         # cache=Depends(get_cache)
#                         ):
#     match_host = get_match_region_host(region=body["current_region"])
#     pass


# # TODO: remote event bus
# # TODO: resume_info: Dict >> resume_info 是 "ContactResume".resume_info (Dict/JSON, 是 Contact!!)
# @router.put("/{company_id}/jobs/{job_id}/resumes/{resume_id}/reply/remote")
# def remote_reply_resume(company_id: int, job_id: int, resume_id: int, body=Depends(resume_request_body),
#                         requests=Depends(get_service_requests),
#                         # cache=Depends(get_cache)
#                         ):
#     match_host = get_match_region_host(region=body["current_region"])
#     pass


@router.get("/{company_id}/resumes/follow-and-apply")
def get_followed_and_contact_resumes(company_id: int, resume_id: int, size: int,
                                     match_host=Depends(get_match_host),
                                     requests=Depends(get_service_requests),
                                     # cache=Depends(get_cache)
                                     ):
    data, err = requests.get(
        url=f"{match_host}/companies/{company_id}/resumes/follow-and-apply",
        params={
            "resume_id": int(resume_id),
            "size": int(size)
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


# TODO: resume_info: Dict >> resume_info 是 FollowResume.resume_info (Dict/JSON)
@router.put("/{company_id}/resumes/{resume_id}/follow/{follow}")
def upsert_follow_resume(company_id: int, resume_id: int, follow: bool, resume_info: Dict = Body(None),
                         match_host=Depends(get_match_host),
                         requests=Depends(get_service_requests),
                         # cache=Depends(get_cache)
                         ):
    # TODO: why "resume_info"??? it's an upsert operation
    data, err = requests.put(
        url=f"{match_host}/companies/{company_id}/resumes/{resume_id}/follow/{follow}",
        json=resume_info)

    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


@router.get("/{company_id}/matchdata")
def get_matchdata(
    company_id: int,
    match_host=Depends(get_match_host),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    data, err = requests.get(
        url=f"{match_host}/companies/{company_id}/matchdata")
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)
