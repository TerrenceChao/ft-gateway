import os
import time
import json
from typing import List, Dict, Any
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from ..req.authorization import AuthRoute, token_required, verify_token_by_teacher_profile
from ..req.teacher_validation import *
from ..res.response import *
from ...domains.match.teacher.value_objects import t_value_objects as vo
from ...domains.match.teacher.services.teacher_service import TeacherProfileService, TeacherAggregateService
from ...domains.match.teacher.services.teacher_resume_service import TeacherResumeService
from ...domains.match.teacher.services.follow_and_contact_job_service import FollowJobService, ContactJobService
from ...apps.resources.adapters import service_client, gw_cache
from ...configs.conf import \
    MY_STATUS_OF_TEACHER_APPLY, STATUS_OF_TEACHER_APPLY, MY_STATUS_OF_TEACHER_REACTION, STATUS_OF_TEACHER_REACTION
from ...configs.constants import Apply
from ...configs.conf import REGION_HOST_MATCH
from ...configs.exceptions import ClientException, \
    NotFoundException, \
    ServerException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


router = APIRouter(
    prefix="/match/teachers",
    tags=["Match Teachers"],
    # dependencies=[Depends(token_required)],
    # route_class=AuthRoute,
    responses={404: {"description": "Not found"}},
)


def get_match_host():
    return REGION_HOST_MATCH


TEACHER = 'teacher'
_teacher_profile_service = TeacherProfileService(service_client)
_teacher_resume_service = TeacherResumeService(service_client)
_follow_job_service = FollowJobService(
    service_client,
    gw_cache,
)
_contact_job_service = ContactJobService(
    service_client,
    gw_cache,
)
_teacher_aggregate_service = TeacherAggregateService(
    service_client,
    gw_cache,
)


"""[此 API 在一開始註冊時會用到]
Returns:
    [Teacher]: [description]
"""

"""[profile]"""


@router.post("/{teacher_id}",
             responses=post_response(f'{TEACHER}.create_profile', vo.TeacherProfileVO),
             status_code=201)
async def create_profile(teacher_id: int,
                   profile: vo.TeacherProfileVO,
                   match_host=Depends(get_match_host),
                   #    verify=Depends(verify_token_by_teacher_profile),
                   ):
    data = await _teacher_profile_service.create_profile(
        host=match_host, teacher_id=teacher_id, profile=profile)
    return post_success(data=data)


@router.get("/{teacher_id}", 
            responses=idempotent_response(f'{TEACHER}.get_profile', vo.TeacherProfileVO))
async def get_profile(teacher_id: int, match_host=Depends(get_match_host)):
    data = await _teacher_profile_service.get_profile(
        host=match_host, teacher_id=teacher_id)
    return res_success(data=data)


@router.put("/{teacher_id}", 
            responses=idempotent_response(f'{TEACHER}.update_profile', vo.TeacherProfileVO))
async def update_profile(teacher_id: int,
                   profile: vo.UpdateTeacherProfileVO = Body(...),
                   match_host=Depends(get_match_host),
                   ):
    data = await _teacher_profile_service.update_profile(
        host=match_host, teacher_id=teacher_id, profile=profile)
    return res_success(data=data)


"""[resume]"""


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.post("/{teacher_id}/resumes",
             responses=post_response(f'{TEACHER}.create_resume', vo.TeacherProfileAndResumeVO),
             status_code=201)
async def create_resume(teacher_id: int,
                  profile: vo.UpdateTeacherProfileVO = Body(
                      None, embed=True),  # Nullable
                  resume: vo.ResumeVO = Depends(
                      create_resume_check_resume),
                  register_region: str = Header(...),
                  match_host=Depends(get_match_host),
                  ):
    data = await _teacher_resume_service.create_resume(
        host=match_host, register_region=register_region, teacher_id=teacher_id, resume=resume, profile=profile)
    return post_success(data=data)


# TODO: 當 route pattern 一樣时，明确的 route 要先执行("/{teacher_id}/resumes/brief")，
# 然后才是有变量的 ("/{teacher_id}/resumes/{resume_id}")
@router.get("/{teacher_id}/brief-resumes",
            responses=idempotent_response(f'{TEACHER}.get_brief_resumes', vo.ResumeListVO))
async def get_brief_resumes(teacher_id: int,
                      match_host=Depends(get_match_host),
                      ):
    data = await _teacher_resume_service.get_brief_resumes(
        host=match_host, teacher_id=teacher_id)
    return res_success(data=data)


@router.get("/{teacher_id}/resumes/{resume_id}",
            responses=idempotent_response(f'{TEACHER}.get_resume', vo.TeacherProfileAndResumeVO))
async def get_resume(teacher_id: int,
               resume_id: int,
               match_host=Depends(get_match_host),
               ):
    data = await _teacher_resume_service.get_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id)
    return res_success(data=data)


# TODO: 未来如果允许使用多个 resumes, 需要考虑 idempotent
@router.put("/{teacher_id}/resumes/{resume_id}",
            responses=idempotent_response(f'{TEACHER}.update_resume', vo.TeacherProfileAndResumeVO))
async def update_resume(teacher_id: int,
                  resume_id: int,
                  profile: vo.UpdateTeacherProfileVO = Body(
                      None, embed=True),  # Nullable
                  resume: vo.UpdateResumeVO = Body(
                      None, embed=True),  # Nullable
                  match_host=Depends(get_match_host),
                  ):
    data = await _teacher_resume_service.update_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id, resume=resume, profile=profile)
    return res_success(data=data)


"""[可见度]
TODO: 未来如果允许使用多个 resumes:
A. 可以将 resumes 设置为一主多备 (只采用一个，其他为备用)
  enable=True:  resume.rid=rid 设置为 True, 其他设置为 False
  enable=False: 所有 resume 设置为 False
"""  


@router.put("/{teacher_id}/resumes/{resume_id}/enable/{enable}",
            responses=idempotent_response(f'{TEACHER}.enable_resume', vo.EnableResumeVO))
async def enable_resume(teacher_id: int,
                  resume_id: int,
                  enable: bool,
                  match_host=Depends(get_match_host),
                  ):
    data = await _teacher_resume_service.enable_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id, enable=enable)
    return res_success(data=data)


@router.delete("/{teacher_id}/resumes/{resume_id}",
               responses=idempotent_response(f'{TEACHER}.delete_resume', bool))
async def delete_resume(teacher_id: int,
                  resume_id: int,
                  match_host=Depends(get_match_host)
                  ):
    data = await _teacher_resume_service.delete_resume(
        host=match_host, teacher_id=teacher_id, resume_id=resume_id)
    return res_success(data=data)


"""[resume section]"""

@router.put("/{teacher_id}/resumes/{resume_id}/sections",
             responses=post_response(f'{TEACHER}.upsert_resume_section', vo.ReturnResumeSectionVO))
async def create_or_update_resume_section(
    resume_section: vo.ResumeSectionVO = Depends(upsert_resume_section_check),
    match_host=Depends(get_match_host),
):
    data = None
    # TODO: refresh Resume.updated_at
    data = await _teacher_resume_service.upsert_resume_section(
        host=match_host, resume_section=resume_section)
    return res_success(data=data, msg=resume_section.upsert_msg())


@router.delete("/{teacher_id}/resumes/{resume_id}/sections/{section_id}",
             responses=post_response(f'{TEACHER}.delete_resume_section', bool))
async def delete_resume_section(
    teacher_id: int,
    resume_id: int,
    section_id: int,
    match_host=Depends(get_match_host),
):
    data = None
    # TODO: refresh Resume.updated_at
    data = await _teacher_resume_service.delete_resume_section(
        host=match_host,
        teacher_id=teacher_id,
        resume_id=resume_id,
        section_id=section_id,
    )
    return res_success(data=data)


"""[follow-job]"""


@router.put("/{teacher_id}/job-follows/{job_id}",
            responses=idempotent_response(f'{TEACHER}.upsert_follow_job', vo.FollowJobVO))
async def upsert_follow_job(teacher_id: int,
                      job_id: int,
                      job_info: vo.BaseJobVO = Body(...),
                      match_host=Depends(get_match_host),
                      ):
    data = await _follow_job_service.upsert_follow_job(
        host=match_host, teacher_id=teacher_id, job_id=job_id, job_info=job_info)

    return res_success(data=data)


@router.get("/{teacher_id}/job-follows",
            responses=idempotent_response(f'{TEACHER}.get_followed_job_list', vo.FollowJobListVO))
async def get_followed_job_list(teacher_id: int,
                          size: int = Query(10),
                          next_ts: int = Query(0),
                          match_host=Depends(get_match_host),
                          ):
    data = await _follow_job_service.get_followed_job_list(
        host=match_host, teacher_id=teacher_id, size=size, next_ts=next_ts)

    return res_success(data=data)


@router.delete("/{teacher_id}/job-follows/{job_id}",
               responses=idempotent_response(f'{TEACHER}.delete_followed_job', bool))
async def delete_followed_job(teacher_id: int,
                        job_id: int,
                        match_host=Depends(get_match_host),
                        ):
    data = await _follow_job_service.delete_followed_job(
        host=match_host, teacher_id=teacher_id, job_id=job_id)

    return res_success(data=data)


"""[contact-job]"""


# TODO: job_info: Dict >> job_info 是 "ContactJob".job_info (Dict/JSON, 是 Contact!!)
@router.put("/{teacher_id}/apply-job",
            responses=idempotent_response(f'{TEACHER}.apply_job', vo.ContactJobVO))
async def apply_job(teacher_id: int = Path(...),
              body: vo.ApplyJobVO = Depends(apply_job_check),
              match_host=Depends(get_match_host),
              ):
    contact_job = await _contact_job_service.apply_job(
        host=match_host, teacher_id=teacher_id, body=body)

    return res_success(data=contact_job)


@router.get("/{teacher_id}/job-applications",
            responses=idempotent_response(f'{TEACHER}.get_applied_job_list', vo.ContactJobListVO))
async def get_applied_job_list(teacher_id: int = Path(...),
                         size: int = Query(10),
                         next_ts: int = Query(0),
                         match_host=Depends(get_match_host),
                         ):
    # APPLY
    my_statuses: List[str] = MY_STATUS_OF_TEACHER_APPLY
    statuses: List[str] = STATUS_OF_TEACHER_APPLY
    data = await _contact_job_service.get_any_contacted_job_list(
        host=match_host,
        teacher_id=teacher_id,
        my_statuses=my_statuses,
        statuses=statuses,
        size=size,
        next_ts=next_ts,
    )
    return res_success(data=data)


@router.get("/{teacher_id}/job-positions",
            responses=idempotent_response(f'{TEACHER}.get_job_position_list', vo.ContactJobListVO))
async def get_job_position_list(teacher_id: int = Path(...),
                          size: int = Query(10),
                          next_ts: int = Query(0),
                          match_host=Depends(get_match_host),
                          ):
    # REACTION
    my_statuses: List[str] = MY_STATUS_OF_TEACHER_REACTION
    statuses: List[str] = STATUS_OF_TEACHER_REACTION
    data = await _contact_job_service.get_any_contacted_job_list(
        host=match_host,
        teacher_id=teacher_id,
        my_statuses=my_statuses,
        statuses=statuses,
        size=size,
        next_ts=next_ts,
    )
    return res_success(data=data)


@router.delete("/{teacher_id}/job-contacts/{job_id}",
               responses=idempotent_response(f'{TEACHER}.delete_any_contacted_job', bool))
async def delete_any_contacted_job(teacher_id: int,
                             job_id: int,
                             match_host=Depends(get_match_host),
                             ):
    data = await _contact_job_service.delete_any_contacted_job(
        host=match_host, teacher_id=teacher_id, job_id=job_id)

    return res_success(data=data)


"""[others]"""


@router.get("/{teacher_id}/follow-and-application/jobs",
            responses=idempotent_response(f'{TEACHER}.get_follows_and_applications_at_first', vo.TeacherFollowAndContactVO))
async def get_follows_and_applications_at_first(teacher_id: int,
                                          size: int = Query(10),
                                          match_host=Depends(get_match_host),
                                          ):
    data = await _teacher_aggregate_service.get_job_follows_and_contacts(
        host=match_host, teacher_id=teacher_id, size=size)

    return res_success(data=data)


@router.get("/{teacher_id}/matchdata",
            responses=idempotent_response(f'{TEACHER}.get_matchdata', vo.TeacherMatchDataVO))
async def get_matchdata(teacher_id: int,
                  size: int = Query(10),
                  match_host=Depends(get_match_host),
                  ):
    data = await _teacher_aggregate_service.get_matchdata(
        host=match_host, teacher_id=teacher_id, size=size)

    return res_success(data=data)
