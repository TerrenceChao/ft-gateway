import os
import time
import json
from typing import List, Dict, Any
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from ..req.authorization import AuthRoute, token_required, verify_token_by_company_profile
from ..req.company_validation import *
from ..res.response import *
from ...domains.match.company.value_objects import c_value_objects as vo
from ...domains.match.company.services.company_service import CompanyProfileService, CompanyAggregateService
from ...domains.match.company.services.company_job_service import CompanyJobService
from ...domains.match.company.services.follow_and_contact_resume_service import FollowResumeService, ContactResumeService
from ...domains.match.teacher.services.teacher_service import TeacherProfileService
from ...domains.payment.services.payment_service import PaymentService
from ...domains.notify.value_objects import email_value_objects as email_vo
from ...configs.service_client import service_client
from ...configs.cache import gw_cache
from ...configs.conf import \
    MY_STATUS_OF_COMPANY_APPLY, STATUS_OF_COMPANY_APPLY, MY_STATUS_OF_COMPANY_REACTION, STATUS_OF_COMPANY_REACTION
from ...configs.constants import Apply
from ...configs.region_hosts import *
from ...configs.exceptions import ClientException, \
    NotFoundException, \
    ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix="/match/companies",
    tags=["Match Companies"],
    dependencies=[Depends(token_required)],
    route_class=AuthRoute,
    responses={404: {"description": "Not found"}},
)


def get_match_host(current_region: str = Header(...)):
    return get_match_region_host(region=current_region)

def get_payment_host(current_region: str = Header(...)):
    return get_payment_region_host(region=current_region)

def get_auth_host(register_region: str = Header(...)):
    return get_auth_region_host(region=register_region)


COMPANY = 'company'
_payment_service = PaymentService(
    service_client, 
    gw_cache,
)
_company_profile_service = CompanyProfileService(service_client)
_company_job_service = CompanyJobService(service_client)
_follow_resume_service = FollowResumeService(
    service_client,
    gw_cache,
)
_contact_resume_service = ContactResumeService(
    service_client,
    gw_cache,
    _payment_service,
)
_company_aggregate_service = CompanyAggregateService(
    service_client,
    gw_cache,
)
_payment_service = PaymentService(
    service_client, 
    gw_cache,
)


"""[此 API 在一開始註冊時會用到]
Returns:
    [Company]: [description]
"""

"""[profile]"""


@router.post("/{company_id}",
             responses=post_response(f'{COMPANY}.create_profile', vo.CompanyProfileVO),
             status_code=201)
def create_profile(company_id: int,
                   profile: vo.CompanyProfileVO,
                   match_host=Depends(get_match_host),
                   #    verify=Depends(verify_token_by_company_profile),
                   ):
    data = _company_profile_service.create_profile(
        host=match_host, company_id=company_id, profile=profile)
    return res_success(data=data)


@router.get("/{company_id}", 
            responses=idempotent_response(f'{COMPANY}.get_profile', vo.CompanyProfileVO))
def get_profile(company_id: int, match_host=Depends(get_match_host)):
    data = _company_profile_service.get_profile(
        host=match_host, company_id=company_id)
    return res_success(data=data)


@router.put("/{company_id}", 
            responses=idempotent_response(f'{COMPANY}.update_profile', vo.CompanyProfileVO))
def update_profile(company_id: int,
                   profile: vo.UpdateCompanyProfileVO = Body(...),
                   match_host=Depends(get_match_host),
                   ):
    data = _company_profile_service.update_profile(
        host=match_host, company_id=company_id, profile=profile)
    return res_success(data=data)


"""[job]"""


# TODO: 未來如果允許使用多個 jobs, 須考慮 idempotent
@router.post("/{company_id}/jobs",
             responses=post_response(f'{COMPANY}.create_job', vo.CompanyProfileAndJobVO),
             status_code=201)
def create_job(company_id: int,
               profile: vo.UpdateCompanyProfileVO = Body(
                   None, embed=True),  # Nullable
               job: vo.JobVO = Depends(create_job_check_job),
               register_region: str = Header(...),
               match_host=Depends(get_match_host),
               ):
    data = _company_job_service.create_job(
        host=match_host, register_region=register_region, company_id=company_id, job=job, profile=profile)
    return res_success(data=data)


# TODO: 當 route pattern 一樣時，明確的 route 要先執行("/{company_id}/jobs/brief")，
# 然後才是有變數的 ("/{company_id}/jobs/{job_id}")
@router.get("/{company_id}/brief-jobs",
            responses=idempotent_response(f'{COMPANY}.get_brief_jobs', vo.JobListVO))
def get_brief_jobs(company_id: int,
                   size: int = Query(None),
                   job_id: int = Query(None),
                   match_host=Depends(get_match_host),
                   ):
    data = _company_job_service.get_brief_jobs(
        host=match_host, company_id=company_id, size=size, job_id=job_id)
    return res_success(data=data)


@router.get("/{company_id}/jobs/{job_id}",
            responses=idempotent_response(f'{COMPANY}.get_job', vo.CompanyProfileAndJobVO))
def get_job(company_id: int,
            job_id: int,
            match_host=Depends(get_match_host),
            ):
    data = _company_job_service.get_job(
        host=match_host, company_id=company_id, job_id=job_id)
    return res_success(data=data)


# TODO: 未來如果允許使用多個 resumes, 須考慮 idempotent
@router.put("/{company_id}/jobs/{job_id}",
            responses=idempotent_response(f'{COMPANY}.update_job', vo.CompanyProfileAndJobVO))
def update_job(company_id: int,
               job_id: int,
               profile: vo.UpdateCompanyProfileVO = Body(
                   None, embed=True),  # Nullable
               job: vo.UpdateJobVO = Body(
                   None, embed=True),  # Nullable,
               match_host=Depends(get_match_host),
               ):
    data = _company_job_service.update_job(
        host=match_host, company_id=company_id, job_id=job_id, job=job, profile=profile)
    return res_success(data=data)


"""[可見度]
TODO: 未來如果允許使用多個 jobs:
A. 可以將 jobs 設定為一主多備 (只採用一個，其他為備用)
  enable=True:  job.id=jid 設為 True, 其它設為 False
  enable=False: 所有 job 設為 False
  
B. 可同時使用多個 jobs. 針對不同 teacher/resume 配對不同 job
"""


@router.put("/{company_id}/jobs/{job_id}/enable/{enable}",
            responses=idempotent_response(f'{COMPANY}.enable_job', vo.EnableJobVO))
def enable_job(company_id: int,
               job_id: int,
               enable: bool,
               match_host=Depends(get_match_host),
               ):
    data = _company_job_service.enable_job(
        host=match_host, company_id=company_id, job_id=job_id, enable=enable)
    return res_success(data=data)


@router.delete("/{company_id}/jobs/{job_id}",
               responses=idempotent_response(f'{COMPANY}.delete_job', bool))
def delete_job(company_id: int,
               job_id: int,
               match_host=Depends(get_match_host)
               ):
    data = _company_job_service.delete_job(
        host=match_host, company_id=company_id, job_id=job_id)
    return res_success(data=data)


"""[follow-resume]"""


@router.put("/{company_id}/resume-follows/{resume_id}",
            responses=idempotent_response(f'{COMPANY}.upsert_follow_resume', vo.FollowResumeVO))
def upsert_follow_resume(company_id: int,
                         resume_id: int,
                         resume_info: vo.BaseResumeVO = Body(None),
                         match_host=Depends(get_match_host),
                         ):
    data = _follow_resume_service.upsert_follow_resume(
        host=match_host, company_id=company_id, resume_id=resume_id, resume_info=resume_info)

    return res_success(data=data)


@router.get("/{company_id}/resume-follows",
            responses=idempotent_response(f'{COMPANY}.get_followed_resume_list', vo.FollowResumeListVO))
def get_followed_resume_list(company_id: int,
                             size: int,
                             next_ts: int = None,
                             match_host=Depends(get_match_host),
                             ):
    data = _follow_resume_service.get_followed_resume_list(
        host=match_host, company_id=company_id, size=size, next_ts=next_ts)

    return res_success(data=data)


# @router.get("/{company_id}/resume-follows/{resume_id}",
#             responses=idempotent_response(f'{COMPANY}.get_followed_resume', vo.FollowResumeVO))
# def get_followed_resume(company_id: int, resume_id: int,
#                         match_host=Depends(get_match_host),
#                         ):
#     pass


@router.delete("/{company_id}/resume-follows/{resume_id}",
               responses=idempotent_response(f'{COMPANY}.delete_followed_resume', bool))
def delete_followed_resume(company_id: int,
                           resume_id: int,
                           match_host=Depends(get_match_host),
                           ):
    data = _follow_resume_service.delete_followed_resume(
        host=match_host, company_id=company_id, resume_id=resume_id)

    return res_success(data=data)


"""[contact-resume]"""


@router.post("/{company_id}/contact/email")
def contact_teacher_by_email(
                 body: email_vo.EmailVO = Depends(contact_teacher_by_email_check),
                 match_host=Depends(get_match_host),
                 auth_host=Depends(get_auth_host),
                 ):
    teacher_profile = TeacherProfileService.get(service_client, match_host, body.recipient_id)
    data = _contact_resume_service.contact_teacher_by_email(
        auth_host=auth_host, 
        body=body,
        teacher_profile_email=teacher_profile.email if teacher_profile != None else None
    )
    return res_success(data=data)


# TODO: resume_info: Dict >> resume_info 是 "ContactResume".resume_info (Dict/JSON, 是 Contact!!)
@router.put("/{company_id}/apply-resume",
            responses=idempotent_response(f'{COMPANY}.apply_resume', vo.ContactResumeVO))
def apply_resume(company_id: int = Path(...),
                 payment_host=Depends(get_payment_host),
                 body: vo.ApplyResumeVO = Depends(apply_resume_check),
                 match_host=Depends(get_match_host),
                 ):
    contact_resume = _contact_resume_service.apply_resume(
        host=match_host, payment_host=payment_host, company_id=company_id, body=body)

    return res_success(data=contact_resume)


@router.get("/{company_id}/resume-contacts",
            responses=idempotent_response(f'{COMPANY}.get_applied_resume_list', vo.ContactResumeListVO))
def get_applied_resume_list(company_id: int = Path(...),
                              size: int = Query(None),
                              next_ts: int = Query(None),
                              match_host=Depends(get_match_host),
                              ):
    # APPLY
    my_statuses: List[str] = MY_STATUS_OF_COMPANY_APPLY
    statuses: List[str] = STATUS_OF_COMPANY_APPLY
    data = _contact_resume_service.get_any_contacted_resume_list(
        host=match_host,
        company_id=company_id,
        my_statuses=my_statuses,
        statuses=statuses,
        size=size,
        next_ts=next_ts,
    )
    return res_success(data=data)


@router.get("/{company_id}/resume-applications",
            responses=idempotent_response(f'{COMPANY}.get_resume_application_list', vo.ContactResumeListVO))
def get_resume_application_list(company_id: int = Path(...),
                                size: int = Query(None),
                                next_ts: int = Query(None),
                                match_host=Depends(get_match_host),
                                ):
    # REACTION
    my_statuses: List[str] = MY_STATUS_OF_COMPANY_REACTION
    statuses: List[str] = STATUS_OF_COMPANY_REACTION
    data = _contact_resume_service.get_any_contacted_resume_list(
        host=match_host,
        company_id=company_id,
        my_statuses=my_statuses,
        statuses=statuses,
        size=size,
        next_ts=next_ts,
    )
    return res_success(data=data)


@router.delete("/{company_id}/resume-contacts/{resume_id}",
               responses=idempotent_response(f'{COMPANY}.delete_any_contacted_resume', bool))
def delete_any_contacted_resume(company_id: int,
                                resume_id: int,
                                match_host=Depends(get_match_host),
                                ):
    data = _contact_resume_service.delete_any_contacted_resume(
        host=match_host, company_id=company_id, resume_id=resume_id)

    return res_success(data=data)


"""[others]"""


@router.get("/{company_id}/follow-and-contact/resumes",
            responses=idempotent_response(f'{COMPANY}.get_follows_and_contacts_at_first', vo.CompanyFollowAndContactVO))
def get_follows_and_contacts_at_first(company_id: int,
                                      size: int = None,
                                      match_host=Depends(get_match_host),
                                      ):
    data = _company_aggregate_service.get_resume_follows_and_contacts(
        host=match_host, company_id=company_id, size=size)

    return res_success(data=data)


@router.get("/{company_id}/matchdata",
            responses=idempotent_response(f'{COMPANY}.get_matchdata', vo.CompanyMatchDataVO))
def get_matchdata(company_id: int,
                  size: int = None,
                  match_host=Depends(get_match_host),
                  ):
    data = _company_aggregate_service.get_matchdata(
        host=match_host, company_id=company_id, size=size)

    return res_success(data=data)
