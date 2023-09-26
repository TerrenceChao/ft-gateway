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
from ...infra.db.nosql import match_teachers_schemas as schemas
from ..req.authorization import AuthMatchRoute, token_required, verify_token_by_teacher_profile
from ..res.response import res_success, response_vo
from ...domains.match.teacther.services.teacher_profile_service import TeacherProfileService
from ...domains.match.teacther.services.teacher_resume_service import TeacherResumeService
from ...apps.service_api_dapter import ServiceApiAdapter, get_service_requests
from ...configs.constants import Apply
from ...configs.region_hosts import get_match_region_host
from ...configs.exceptions import ClientException, \
    NotFoundException, \
    ServerException
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


_teacher_profile_service = TeacherProfileService(ServiceApiAdapter(requests))
_teacher_resume_service = TeacherResumeService(ServiceApiAdapter(requests))


"""[此 API 在一開始註冊時會用到]
Returns:
    [Teacher]: [description]
"""


@router.post("/",
             response_model=response_vo(
                 "t_create_profile", schemas.TeacherProfile),
             status_code=201)
def create_profile(profile: schemas.TeacherProfile,
                   match_host=Depends(get_match_host),
                   verify=Depends(verify_token_by_teacher_profile),
                   ):
    data = _teacher_profile_service.create_profile(
        host=match_host, profile=profile)
    return res_success(data=data)


@router.get("/{teacher_id}", response_model=response_vo("t_get_profile", schemas.SoftTeacherProfile))
def get_profile(teacher_id: int, match_host=Depends(get_match_host)):
    data = _teacher_profile_service.get_profile(
        host=match_host, teacher_id=teacher_id)
    return res_success(data=data)


@router.put("/{teacher_id}", response_model=response_vo("t_update_profile", schemas.SoftTeacherProfile))
def update_profile(teacher_id: int,
                   profile: schemas.SoftTeacherProfile = Body(...),
                   match_host=Depends(get_match_host),
                   ):
    data = _teacher_profile_service.update_profile(
        host=match_host, teacher_id=teacher_id, profile=profile)
    return res_success(data=data)


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.post("/{teacher_id}/resumes",
             response_model=response_vo(
                 "t_create_resume", schemas.UpsertTeacherProfileResume),
             status_code=201)
def create_resume(teacher_id: int,
                  profile: schemas.TeacherProfile = Body(
                      None, embed=True),  # Nullable
                  resume: schemas.Resume = Body(..., embed=True),
                  register_region: str = Header(...),
                  match_host=Depends(get_match_host),
                  ):
    data = _teacher_resume_service.create_resume(
        host=match_host, register_region=register_region, teacher_id=teacher_id, resume=resume, profile=profile)
    return res_success(data=data)


# TODO: 當 route pattern 一樣時，明確的 route 要先執行("/{teacher_id}/resumes/brief")，
# 然後才是有變數的 ("/{teacher_id}/resumes/{resume_id}")
@router.get("/{teacher_id}/resumes/brief")
def get_brief_resumes(teacher_id: int,
                      match_host=Depends(get_match_host),
                      ):
    data = _teacher_resume_service.get_brief_resumes(
        host=match_host, teacher_id=teacher_id)
    return res_success(data=data)


@router.get("/{teacher_id}/resumes/{resume_id}")
def get_resume(teacher_id: int, resume_id: int,
               match_host=Depends(get_match_host),
               ):
    data = _teacher_resume_service.get_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id)
    return res_success(data=data)


# # TODO: deprecated
# @router.get("/{teacher_id}/resumes")
# def get_resumes(teacher_id: int):
#   pass


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.put("/{teacher_id}/resumes/{resume_id}",
            response_model=response_vo("t_update_resume", schemas.UpsertTeacherProfileResume))
def update_resume(teacher_id: int,
                  resume_id: int,
                  profile: schemas.SoftTeacherProfile = Body(
                      None, embed=True),  # Nullable
                  resume: schemas.SoftResume = Body(None, embed=True),  # Nullable
                  match_host=Depends(get_match_host),
                  ):
    data = _teacher_resume_service.update_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id, resume=resume, profile=profile)
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
                  ):
    data = _teacher_resume_service.enable_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id, enable=enable)
    return res_success(data=data)


@router.delete("/{teacher_id}/resumes/{resume_id}")
def delete_resume(teacher_id: int, resume_id: int, match_host=Depends(get_match_host)):
    data = _teacher_resume_service.delete_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id)
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


def job_request_body(register_region: str = Header(None), current_region: str = Header(...), my_status: Apply = Body(None), status: Apply = Body(None), job: Dict = Body(...), resumeInfo: Dict = Body(...)):
    return {
        "register_region": register_region,
        "current_region": current_region,
        "my_status": my_status,
        "status": status,
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
            "my_status": body["my_status"],
            "status": body["status"],
            "job": body["job"],
            "resumeInfo": body["resumeInfo"],
        },
        headers={
            "register_region": body["register_region"],
            "current_region": body["current_region"],
        })
    if err:
        log.error(f"apply_job fail: [request put], match_host:%s, teacher_id:%s, resume_id:%s, job_id:%s, body:{{%s}}, contact_job:%s, err:%s",
                  match_host, teacher_id, resume_id, job_id, body, contact_job, err)
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
            "my_status": body["my_status"],
            "status": body["status"],
            "job": body["job"],
            "resumeInfo": body["resumeInfo"],
        },
        headers={
            "register_region": body["register_region"],
            "current_region": body["current_region"],
        })
    if err:
        log.error(f"reply_job fail: [request put], match_host:%s, teacher_id:%s, resume_id:%s, job_id:%s, body:{{%s}}, contact_job:%s, err:%s",
                  match_host, teacher_id, resume_id, job_id, body, contact_job, err)
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
        log.error(f"get_followed_and_contact_jobs fail: [request get], match_host:%s, teacher_id:%s, job_id:%s, size:%s, data:%s, err:%s",
                  match_host, teacher_id, job_id, size, data, err)
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
        log.error(f"upsert_follow_job fail: [request put], match_host:%s, teacher_id:%s, job_id:%s, follow:%s, job_info:%s, data:%s, err:%s",
                  match_host, teacher_id, job_id, follow, job_info, data, err)
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
        log.error(f"get_matchdata fail: [request get], match_host:%s, teacher_id:%s, data:%s, err:%s",
                  match_host, teacher_id, data, err)
        raise ServerException(msg=err)

    return res_success(data=data)
