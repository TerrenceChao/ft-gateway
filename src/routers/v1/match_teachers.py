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
from ..req.authorization import AuthMatchRoute, token_required, verify_token_by_teacher_profile
from ..req.teacher_validation import *
from ..res.response import res_success, response_vo
from ..res import teacher_response as teach_res
from ...domains.match.teacher.value_objects import t_value_objects as teach_vo
from ...domains.match.teacher.services.teacher_service import TeacherProfileService, TeacherAggregateService
from ...domains.match.teacher.services.teacher_resume_service import TeacherResumeService
from ...domains.match.teacher.services.follow_and_contact_job_service import FollowJobService, ContactJobService
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
_follow_job_service = FollowJobService(ServiceApiAdapter(requests))
_contact_job_service = ContactJobService(ServiceApiAdapter(requests))
_teacher_aggregate_service = TeacherAggregateService(
    ServiceApiAdapter(requests))


"""[此 API 在一開始註冊時會用到]
Returns:
    [Teacher]: [description]
"""

"""[profile]"""


@router.post("/{teacher_id}",
             response_model=teach_res.TeacherProfileResponseVO,
             status_code=201)
def create_profile(teacher_id: int,
                   profile: teach_vo.TeacherProfileVO,
                   match_host=Depends(get_match_host),
                   #    verify=Depends(verify_token_by_teacher_profile),
                   ):
    data = _teacher_profile_service.create_profile(
        host=match_host, teacher_id=teacher_id, profile=profile)
    return res_success(data=data)


@router.get("/{teacher_id}", response_model=teach_res.TeacherProfileResponseVO)
def get_profile(teacher_id: int, match_host=Depends(get_match_host)):
    data = _teacher_profile_service.get_profile(
        host=match_host, teacher_id=teacher_id)
    return res_success(data=data)


@router.put("/{teacher_id}", response_model=teach_res.TeacherProfileResponseVO)
def update_profile(teacher_id: int,
                   profile: teach_vo.UpdateTeacherProfileVO = Body(...),
                   match_host=Depends(get_match_host),
                   ):
    data = _teacher_profile_service.update_profile(
        host=match_host, teacher_id=teacher_id, profile=profile)
    return res_success(data=data)


"""[resume]"""


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.post("/{teacher_id}/resumes",
             response_model=teach_res.TeacherProfileAndResumeResponseVO,
             status_code=201)
def create_resume(teacher_id: int,
                  profile: teach_vo.UpdateTeacherProfileVO = Body(
                      None, embed=True),  # Nullable
                  resume: teach_vo.ResumeVO = Depends(
                      create_resume_check_resume),
                  register_region: str = Header(...),
                  match_host=Depends(get_match_host),
                  ):
    data = _teacher_resume_service.create_resume(
        host=match_host, register_region=register_region, teacher_id=teacher_id, resume=resume, profile=profile)
    return res_success(data=data)


# TODO: 當 route pattern 一樣時，明確的 route 要先執行("/{teacher_id}/resumes/brief")，
# 然後才是有變數的 ("/{teacher_id}/resumes/{resume_id}")
@router.get("/{teacher_id}/brief-resumes",
            response_model=teach_res.ResumeListResponseVO)
def get_brief_resumes(teacher_id: int,
                      match_host=Depends(get_match_host),
                      ):
    data = _teacher_resume_service.get_brief_resumes(
        host=match_host, teacher_id=teacher_id)
    return res_success(data=data)


@router.get("/{teacher_id}/resumes/{resume_id}",
            response_model=teach_res.TeacherProfileAndResumeResponseVO)
def get_resume(teacher_id: int,
               resume_id: int,
               match_host=Depends(get_match_host),
               ):
    data = _teacher_resume_service.get_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id)
    return res_success(data=data)


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.put("/{teacher_id}/resumes/{resume_id}",
            response_model=teach_res.TeacherProfileAndResumeResponseVO)
def update_resume(teacher_id: int,
                  resume_id: int,
                  profile: teach_vo.UpdateTeacherProfileVO = Body(
                      None, embed=True),  # Nullable
                  resume: teach_vo.UpdateResumeVO = Body(
                      None, embed=True),  # Nullable
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


@router.put("/{teacher_id}/resumes/{resume_id}/enable/{enable}",
            response_model=teach_res.EnableResumeResponseVO)
def enable_resume(teacher_id: int,
                  resume_id: int,
                  enable: bool,
                  match_host=Depends(get_match_host),
                  ):
    data = _teacher_resume_service.enable_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id, enable=enable)
    return res_success(data=data)


@router.delete("/{teacher_id}/resumes/{resume_id}")
def delete_resume(teacher_id: int,
                  resume_id: int,
                  match_host=Depends(get_match_host)
                  ):
    data = _teacher_resume_service.delete_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id)
    return res_success(data=data)


"""[follow-job]"""


@router.put("/{teacher_id}/job-follows/{job_id}",
            response_model=teach_res.FollowJobResponseVO)
def upsert_follow_job(teacher_id: int,
                      job_id: int,
                      job_info: teach_vo.BaseJobVO = Body(...),
                      match_host=Depends(get_match_host),
                      ):
    data = _follow_job_service.upsert_follow_job(
        host=match_host, teacher_id=teacher_id, job_id=job_id, job_info=job_info)

    return res_success(data=data)


@router.get("/{teacher_id}/job-follows",
            response_model=teach_res.FollowJobListResponseVO)
def get_followed_job_list(teacher_id: int,
                          size: int,
                          next_ts: int = None,
                          match_host=Depends(get_match_host),
                          ):
    data = _follow_job_service.get_followed_job_list(
        host=match_host, teacher_id=teacher_id, size=size, next_ts=next_ts)

    return res_success(data=data)


# @router.get("/{teacher_id}/job-follows/{job_id}",
#             response_model=teach_res.FollowJobResponseVO)
# def get_followed_job(teacher_id: int, job_id: int,
#                      match_host=Depends(get_match_host),
#                      requests=Depends(get_service_requests),
#                      ):
#     pass


@router.delete("/{teacher_id}/job-follows/{job_id}")
def delete_followed_job(teacher_id: int,
                        job_id: int,
                        match_host=Depends(get_match_host),
                        ):
    data = _follow_job_service.delete_followed_job(
        host=match_host, teacher_id=teacher_id, job_id=job_id)

    return res_success(data=data)


"""[contact-job]"""


# TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
@router.put("/{teacher_id}/apply-job",
            response_model=teach_res.ContactJobResponseVO)
def apply_job(teacher_id: int = Path(...),
              body: teach_vo.ApplyJobVO = Depends(apply_job_check),
              match_host=Depends(get_match_host),
              ):
    contact_job = _contact_job_service.apply_job(
        host=match_host, teacher_id=teacher_id, body=body)

    return res_success(data=contact_job)


@router.get("/{teacher_id}/job-applications",
            response_model=teach_res.ContactJobListResponseVO)
def get_applied_job_list(teacher_id: int = Path(...),
                         size: int = Query(None),
                         next_ts: int = Query(None),
                         match_host=Depends(get_match_host),
                         ):
    # proactively
    my_statuses: List = [Apply.CONFRIM]
    statuses: List = [Apply.PENDING]
    data = _contact_job_service.get_any_contacted_job_list(
        host=match_host,
        teacher_id=teacher_id,
        my_statuses=my_statuses,
        statuses=statuses,
        size=size,
        next_ts=next_ts,
    )
    return res_success(data=data)


@router.get("/{teacher_id}/job-positions",
            response_model=teach_res.ContactJobListResponseVO)
def get_job_position_list(teacher_id: int = Path(...),
                          size: int = Query(None),
                          next_ts: int = Query(None),
                          match_host=Depends(get_match_host),
                          ):
    # passively
    my_statuses: List = [Apply.PENDING]
    statuses: List = []
    data = _contact_job_service.get_any_contacted_job_list(
        host=match_host,
        teacher_id=teacher_id,
        my_statuses=my_statuses,
        statuses=statuses,
        size=size,
        next_ts=next_ts,
    )
    return res_success(data=data)


@router.delete("/{teacher_id}/job-contacts/{job_id}")
def delete_any_contacted_job(teacher_id: int,
                             job_id: int,
                             match_host=Depends(get_match_host),
                             ):
    data = _contact_job_service.delete_any_contacted_job(
        host=match_host, teacher_id=teacher_id, job_id=job_id)

    return res_success(data=data)


"""[others]"""


@router.get("/{teacher_id}/follow-and-application/jobs",
            response_model=teach_res.TeacherFollowAndContactResponseVO)
def get_follows_and_applications_at_first(teacher_id: int,
                                          size: int = None,
                                          match_host=Depends(get_match_host),
                                          ):
    data = _teacher_aggregate_service.get_job_follows_and_contacts(
        host=match_host, teacher_id=teacher_id, size=size)

    return res_success(data=data)


@router.get("/{teacher_id}/matchdata",
            response_model=teach_res.TeacherMatchDataResponseVO)
def get_matchdata(teacher_id: int,
                  size: int = None,
                  match_host=Depends(get_match_host),
                  ):
    data = _teacher_aggregate_service.get_matchdata(
        host=match_host, teacher_id=teacher_id, size=size)

    return res_success(data=data)
