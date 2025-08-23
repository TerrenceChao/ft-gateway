from typing import List, Dict, Any
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from ...configs.conf import MAX_TAGS
from ...configs.exceptions import ClientException
from ...domains.match.public_value_objects import BaseJobVO
from ...domains.match.teacher.value_objects.t_value_objects import *


def __parse_resume_sections(teacher_id, resume_id, sections):
    if sections != None and len(sections) > 0:
        for section in sections:
            section.tid = teacher_id
            section.rid = resume_id


# def create_resume_check_profile(
#     teacher_id: int = Path(...),
#     profile: UpdateTeacherProfileVO = Body(None, embed=True),  # Nullable
# ) -> (UpdateTeacherProfileVO):
#     # if profile:
#     #     profile.tid = teacher_id
#     return profile


def create_resume_check_resume(
    register_region: str = Header(...), # TODO: vary important!!
    teacher_id: int = Path(...),
    resume: ResumeVO = Body(..., embed=True)
) -> (ResumeVO):
    # resume.tid = teacher_id
    resume.region = register_region
    if len(resume.tags) > MAX_TAGS:
        raise ClientException(msg=f'The number of tags must be less than {MAX_TAGS}.')
    
    # __parse_resume_sections(teacher_id, None, resume.sections)
    return resume


# def update_resume_check_profile(
#     teacher_id: int = Path(...),
#     profile: UpdateTeacherProfileVO = Body(None, embed=True),  # Nullable
# ) -> (UpdateTeacherProfileVO):
#     # if profile:
#     #     profile.tid = teacher_id
#     return profile


def update_resume_check_resume(
    teacher_id: int = Path(...),
    resume_id: int = Path(...),
    resume: UpdateResumeVO = Body(None, embed=True),  # Nullable
) -> (UpdateResumeVO):
    if resume:
        # resume.tid = teacher_id
        # resume.rid = resume_id
        if len(resume.tags) > MAX_TAGS:
            raise ClientException(msg=f'The number of tags must be less than {MAX_TAGS}.')

        # __parse_resume_sections(teacher_id, resume_id, resume.sections)

    return resume

def create_resume_section_check(
    teacher_id: int = Path(...),
    resume_id: int = Path(...),
    resume_section: ResumeSectionVO = Body(...),
):
    resume_section.tid = teacher_id
    resume_section.rid = resume_id
    return resume_section

def upsert_resume_section_check(
    teacher_id: int = Path(...),
    resume_id: int = Path(...),
    resume_section: ResumeSectionVO = Body(...),
):
    resume_section.tid = teacher_id
    resume_section.rid = resume_id
    return resume_section

def upsert_follow_job_check_job(
    job_id: int = Path(...),
    job_info: BaseJobVO = Body(...),
) -> (Dict):
    # job_info.jid = job_id
    return job_info.model_dump()

def apply_job_check(register_region: str = Header(...),
                    current_region: str = Header(...),
                    body: ApplyJobVO = Body(...),
                    ):
    body.current_region = current_region
    body.resume_info.region = register_region
    return body
