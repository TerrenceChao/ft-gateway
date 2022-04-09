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
from ...db.nosql import match_teachers_schemas as schemas
from ..res.response import res_success, res_err
from ...common.cache import get_cache
from ...common.service_requests import get_service_requests
import logging as log


region_match_hosts = {
    # "default": os.getenv("REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "jp": os.getenv("JP_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "ge": os.getenv("EU_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "us": os.getenv("US_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
}

log.basicConfig(level=log.INFO)


router = APIRouter(
    prefix="/match/teachers",
    tags=["Match Teachers"],
    responses={404: {"description": "Not found"}},
)


"""[此 API 在一開始註冊時會用到]
Returns:
    [Company]: [description]
"""
@router.post("/")
def create_profile(profile: schemas.TeacherProfile,
                   current_region: str = Header(...),
                   requests=Depends(get_service_requests),
                   # cache=Depends(get_cache)
                   ):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    data, err = requests.post(url=f"{match_host}/teachers/",
                             json=profile.dict())
    if err:
        return res_err(msg=err)

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
                  current_region: str = Header(...),
                  requests=Depends(get_service_requests),
                  # cache=Depends(get_cache)
                  ):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    data, err = requests.put(
        url=f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}/enable/{enable}")
    if err:
        return res_err(msg=err)

    return res_success(data=data)


@router.get("/{teacher_id}/jobs/follow-and-apply")
def get_followed_and_contact_jobs(teacher_id: int, job_id: int, size: int,
                                  current_region: str = Header(...),
                                  requests=Depends(get_service_requests),
                                  # cache=Depends(get_cache)
                                  ):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    data, err = requests.get(
        url=f"{match_host}/teachers/{teacher_id}/jobs/follow-and-apply",
        params={
            "job_id": int(job_id),
            "size": int(size)
        })
    if err:
        return res_err(msg=err)

    return res_success(data=data)


# TODO: job_info: Dict >> job_info 是 FollowJob.job_info (Dict/JSON)
@router.put("/{teacher_id}/jobs/{job_id}/follow/{follow}")
def upsert_follow_job(teacher_id: int, job_id: int, follow: bool, job_info: Dict = Body(None),
                      current_region: str = Header(...),
                      requests=Depends(get_service_requests),
                      # cache=Depends(get_cache)
                      ):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    # TODO: why "job_info"??? it's an upsert operation
    data, err = requests.put(
        url=f"{match_host}/teachers/{teacher_id}/jobs/{job_id}/follow/{follow}",
        json=job_info)
    
    if err:
        return res_err(msg=err)

    return res_success(data=data)


# TODO: ?? 有需要批次更新 jobs 再實現
@router.put("/{teacher_id}/jobs/follow")
def upsert_follow_jobs(teacher_id: int, jobsInfo: List[schemas.FollowJob] = Body(...),
                       current_region: str = Header(...),
                       requests=Depends(get_service_requests),
                       # cache=Depends(get_cache)
                       ):
    # TODO: for remote batch update; job's'Info 是多個 FollowJob
    pass


@router.get("/{teacher_id}/resumes/brief")
def get_brief_resumes(teacher_id: int,
                      current_region: str = Header(...),
                      requests=Depends(get_service_requests),
                      # cache=Depends(get_cache)
                      ):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    data, err = requests.get(
        url=f"{match_host}/teachers/{teacher_id}/resumes/brief")
    
    print(data)
    if err:
        return res_err(msg=err)

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
              # current_region: str = Header(...),
              requests=Depends(get_service_requests),
              # cache=Depends(get_cache)
              ):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
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
        return res_err(msg=err)

    return res_success(data=contact_job)


# TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
@router.put("/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/reply")
def reply_job(teacher_id: int, resume_id: int, job_id: int, body=Depends(job_request_body),
              # current_region: str = Header(...),
              requests=Depends(get_service_requests),
              # cache=Depends(get_cache)
              ):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
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
        return res_err(msg=err)

    return res_success(data=contact_job)


# TODO: remote event bus
# TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
@router.put("/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/apply/remote")
def remote_apply_job(teacher_id: int, resume_id: int, job_id: int, body=Depends(job_request_body),
                     # current_region: str = Header(...),
                     requests=Depends(get_service_requests),
                     # cache=Depends(get_cache)
                     ):
    pass


# TODO: remote event bus
# TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
@router.put("/{teacher_id}/resumes/{resume_id}/jobs/{job_id}/reply/remote")
def remote_reply_job(teacher_id: int, resume_id: int, job_id: int, body=Depends(job_request_body),
                     # current_region: str = Header(...),
                     requests=Depends(get_service_requests),
                     # cache=Depends(get_cache)
                     ):
    pass


# # TODO: deprecated
# @router.get("/{teacher_id}/resumes")
# def get_resumes(teacher_id: int):
#   pass



@router.get("/{teacher_id}/resumes/{resume_id}")
def get_resume(teacher_id: int, resume_id: int,
               current_region: str = Header(...),
               requests=Depends(get_service_requests),
               # cache=Depends(get_cache)
               ):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    data, err = requests.get(
        url=f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}")
    if err:
        return res_err(msg=err)

    return res_success(data=data)


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.post("/{teacher_id}/resumes")
def create_resume(
    teacher_id: int,
    profile: schemas.TeacherProfile = Body(None, embed=True),  # Nullable
    resume: schemas.Resume = Body(..., embed=True),
    current_region: str = Header(...),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    data, err = requests.post(
        url=f"{match_host}/teachers/{teacher_id}/resumes",
        json={
            "profile": None if profile == None else profile.dict(),
            "resume": resume.dict()
        })
    if err:
        return res_err(msg=err)

    return res_success(data=data)


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.put("/{teacher_id}/resumes/{resume_id}")
def update_resume(
    teacher_id: int,
    resume_id: int,
    profile: schemas.TeacherProfile = Body(None, embed=True),  # Nullable
    resume: schemas.Resume = Body(None, embed=True),  # Nullable
    current_region: str = Header(...),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    if profile == None and resume == None:
        return res_err(msg="at least one of the profile and resume is required")

    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    data, err = requests.put(
        url=f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}",
        json={
            "profile": profile.dict(),
            "resume": resume.dict()
        })
    if err:
        return res_err(msg=err)

    return res_success(data=data)


@router.get("/{teacher_id}/matchdata")
def get_matchdata(
    teacher_id: int,
    current_region: str = Header(...),
    requests=Depends(get_service_requests),
    # cache=Depends(get_cache)
):
    current_region = current_region.lower()
    match_host = region_match_hosts[current_region]
    data, err = requests.get(
        url=f"{match_host}/teachers/{teacher_id}/matchdata")
    if err:
        return res_err(msg=err)

    return res_success(data=data)
