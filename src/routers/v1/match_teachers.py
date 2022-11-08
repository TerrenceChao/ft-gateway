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
from ...db.nosql import match_teachers_schemas as schemas
from ..req.authorization import AuthMatchRoute, token_required, verify_token_by_teacher_profile
from ..res.response import res_success
from ..res.match_res import response_vo
from ...common.service_requests import get_service_requests
from ...common.region_hosts import get_match_region_host
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix="/match/teachers",
    tags=["Match Teachers"],
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
@router.post("/", 
             response_model=response_vo("t_create_profile", schemas.TeacherProfile), 
             status_code=201)
def create_profile(profile: schemas.TeacherProfile,
                   match_host=Depends(get_match_host),
                   requests=Depends(get_service_requests),
                   # cache=Depends(get_cache),
                   verify=Depends(verify_token_by_teacher_profile),
                   ):
    data, err = requests.post(url=f"{match_host}/teachers/",
                             json=profile.dict())
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.post("/{teacher_id}/resumes", 
             response_model=response_vo("t_create_resume", schemas.UpsertTeacherProfileResume), 
             status_code=201)
def create_resume(
    teacher_id: int,
    profile: schemas.TeacherProfile = Body(None, embed=True),  # Nullable
    resume: schemas.Resume = Body(..., embed=True),
    match_host=Depends(get_match_host),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    data, err = requests.post(
        url=f"{match_host}/teachers/{teacher_id}/resumes",
        json={
            "profile": None if profile == None else profile.dict(),
            "resume": resume.dict()
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


@router.get("/{teacher_id}/resumes/{resume_id}")
def get_resume(teacher_id: int, resume_id: int,
               match_host=Depends(get_match_host),
               requests=Depends(get_service_requests),
               # cache=Depends(get_cache)
               ):
    data, err = requests.get(
        url=f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}")
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


# # TODO: deprecated
# @router.get("/{teacher_id}/resumes")
# def get_resumes(teacher_id: int):
#   pass


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.put("/{teacher_id}/resumes/{resume_id}", 
             response_model=response_vo("t_update_resume", schemas.UpsertTeacherProfileResume))
def update_resume(
    teacher_id: int,
    resume_id: int,
    profile: schemas.TeacherProfile = Body(None, embed=True),  # Nullable
    resume: schemas.Resume = Body(None, embed=True),  # Nullable
    match_host=Depends(get_match_host),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    if profile == None and resume == None:
        raise ClientException(msg="at least one of the profile or resume is required")

    data, err = requests.put(
        url=f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}",
        json={
            "profile": profile.dict(),
            "resume": resume.dict()
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


"""[可見度]
TODO: 未來如果允許使用多個 resumes:
A. 可以將 resumes 設定為一主多備 (只採用一個，其他為備用)
  enable=True:  resume.rid=rid 設為 True, 其它設為 False
  enable=False: 所有 resume 設為 False
  
B. 可同時使用多個 resumes. 針對不同 com/job 投遞不同 resume
"""
@router.put("/{teacher_id}/resumes/{resume_id}/enable/{enable}")
def enable_resume(teacher_id: int, resume_id: int, enable: bool,
                  match_host=Depends(get_match_host),
                  requests=Depends(get_service_requests),
                  # cache=Depends(get_cache)
                  ):
    data, err = requests.put(
        url=f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}/enable/{enable}")
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


# # TODO: ?? 有需要批次更新 jobs 再實現
# @router.put("/{teacher_id}/jobs/follow")
# def upsert_follow_jobs(teacher_id: int, jobsInfo: List[schemas.FollowJob] = Body(...),
#                        match_host=Depends(get_match_host),
#                        requests=Depends(get_service_requests),
#                        # cache=Depends(get_cache)
#                        ):
#     # TODO: for remote batch update; job's'Info 是多個 FollowJob
#     pass


@router.get("/{teacher_id}/resumes/brief")
def get_brief_resumes(teacher_id: int,
                      match_host=Depends(get_match_host),
                      requests=Depends(get_service_requests),
                      # cache=Depends(get_cache)
                      ):
    data, err = requests.get(
        url=f"{match_host}/teachers/{teacher_id}/resumes/brief")
    log.info(data)
    
    
    
    
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)





def job_request_body(register_region: str = Header(None), current_region: str = Header(...), job: Dict = Body(...), resumeInfo: Dict = Body(...)):
    return {
        "register_region": register_region,
        "current_region": current_region,
        "job": job,
        "resumeInfo": resumeInfo
    }


# TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
@router.put("/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/apply")
def apply_job(teacher_id: int, resume_id: int, job_id: int, body=Depends(job_request_body),
              requests=Depends(get_service_requests),
              # cache=Depends(get_cache)
              ):
    match_host = get_match_region_host(region=body["current_region"])
    contact_job, err = requests.put(
        url=f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/apply",
        json={
            "job": body["job"],
            "resumeInfo": body["resumeInfo"]
        },
        headers={
            "register_region": body["register_region"],
            "current_region": body["current_region"]
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=contact_job)


# TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
@router.put("/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/reply")
def reply_job(teacher_id: int, resume_id: int, job_id: int, body=Depends(job_request_body),
              requests=Depends(get_service_requests),
              # cache=Depends(get_cache)
              ):
    match_host = get_match_region_host(region=body["current_region"])
    contact_job, err = requests.put(
        url=f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/reply",
        json={
            "job": body["job"],
            "resumeInfo": body["resumeInfo"]
        },
        headers={
            "register_region": body["register_region"],
            "current_region": body["current_region"]
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=contact_job)


# # TODO: remote event bus
# # TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
# @router.put("/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/apply/remote")
# def remote_apply_job(teacher_id: int, resume_id: int, job_id: int, body=Depends(job_request_body),
#                      requests=Depends(get_service_requests),
#                      # cache=Depends(get_cache)
#                      ):
#     match_host = get_match_region_host(region=body["current_region"])
#     pass


# # TODO: remote event bus
# # TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
# @router.put("/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/reply/remote")
# def remote_reply_job(teacher_id: int, resume_id: int, job_id: int, body=Depends(job_request_body),
#                      requests=Depends(get_service_requests),
#                      # cache=Depends(get_cache)
#                      ):
#     match_host = get_match_region_host(region=body["current_region"])
#     pass


@router.get("/{teacher_id}/jobs/follow-and-apply")
def get_followed_and_contact_jobs(teacher_id: int, job_id: int, size: int,
                                  match_host=Depends(get_match_host),
                                  requests=Depends(get_service_requests),
                                  # cache=Depends(get_cache)
                                  ):
    data, err = requests.get(
        url=f"{match_host}/teachers/{teacher_id}/jobs/follow-and-apply",
        params={
            "job_id": int(job_id),
            "size": int(size)
        })
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


# TODO: job_info: Dict >> job_info 是 FollowJob.job_info (Dict/JSON)
@router.put("/{teacher_id}/jobs/{job_id}/follow/{follow}")
def upsert_follow_job(teacher_id: int, job_id: int, follow: bool, job_info: Dict = Body(None),
                      match_host=Depends(get_match_host),
                      requests=Depends(get_service_requests),
                      # cache=Depends(get_cache)
                      ):
    # TODO: why "job_info"??? it's an upsert operation
    data, err = requests.put(
        url=f"{match_host}/teachers/{teacher_id}/jobs/{job_id}/follow/{follow}",
        json=job_info)
    
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)


@router.get("/{teacher_id}/matchdata")
def get_matchdata(
    teacher_id: int,
    match_host=Depends(get_match_host),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    data, err = requests.get(
        url=f"{match_host}/teachers/{teacher_id}/matchdata")
    if err:
        raise ServerException(msg=err)

    return res_success(data=data)
