from typing import List, Dict, Any
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from ...configs.conf import MAX_TAGS
from ...configs.exceptions import ClientException
from ...domains.match.public_value_objects import BaseResumeVO
from ...domains.match.company.value_objects.c_value_objects import \
    UpdateCompanyProfileVO, JobVO, UpdateJobVO, ApplyResumeVO


# def create_job_check_profile(
#     company_id: int = Path(...),
#     profile: UpdateCompanyProfileVO = Body(None, embed=True),  # Nullable
# ) -> (UpdateCompanyProfileVO):
#     # if profile:
#     #     profile.cid = company_id
#     return profile


def create_job_check_job(
    register_region: str = Header(...), # TODO: vary important!!
    company_id: int = Path(...),
    job: JobVO = Body(..., embed=True),
) -> (JobVO):
    # job.cid = company_id
    job.published_in = register_region
    if len(job.tags) > MAX_TAGS:
        raise ClientException(msg=f'The number of tags must be less than {MAX_TAGS}.')
    
    return job


# def update_job_check_profile(
#     company_id: int = Path(...),
#     profile: UpdateCompanyProfileVO = Body(None, embed=True),  # Nullable
# ) -> (UpdateCompanyProfileVO):
#     # if profile:
#     #     profile.cid = company_id
#     return profile


def update_job_check_job(
    company_id: int = Path(...),
    job_id: int = Path(...),
    job: UpdateJobVO = Body(None, embed=True),  # Nullable
) -> (UpdateJobVO):
    if job:
        # job.cid = company_id
        # job.jid = job_id
        if len(job.tags) > MAX_TAGS:
            raise ClientException(msg=f'The number of tags must be less than {MAX_TAGS}.')
        
    return job


def upsert_follow_resume_check_resume(
    resume_id: int = Path(...),
    resume_info: BaseResumeVO = Body(...),
) -> (Dict):
    # resume_info.rid = resume_id
    return resume_info.dict()


def apply_resume_check(register_region: str = Header(...),
                       current_region: str = Header(...),
                       body: ApplyResumeVO = Body(...)
                       ):
    body.current_region = current_region
    body.job_info.published_in = register_region
    return body
