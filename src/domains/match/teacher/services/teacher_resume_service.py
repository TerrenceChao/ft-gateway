from typing import Any, List, Dict, Optional
from ....service_api import IServiceApi
from .....domains.match.teacher.value_objects import t_value_objects as teach_vo
from .....configs.exceptions import \
    ClientException, ServerException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class TeacherResumeService:
    def __init__(self, req: IServiceApi):
        self.req = req

    async def create_resume(self, host: str, register_region: str, teacher_id: int, resume: teach_vo.ResumeVO, profile: Optional[teach_vo.UpdateTeacherProfileVO] = None):
        resume.region = register_region
        data = await self.req.simple_post(
            url=f"{host}/teachers/{teacher_id}/resumes",
            json={
                "profile": None if profile is None else profile.dict(),
                "resume": resume.dict(),
            })

        return data

    async def get_brief_resumes(self, host: str, teacher_id: int):
        data = await self.req.simple_get(
            url=f"{host}/teachers/{teacher_id}/brief-resumes")
        # log.info(data)

        return data

    async def get_resume(self, host: str, teacher_id: int, resume_id: int):
        data = await self.req.simple_get(
            url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}")

        return data

    async def update_resume(self, host: str, teacher_id: int, resume_id: int, resume: Optional[teach_vo.UpdateResumeVO] = None, profile: Optional[teach_vo.UpdateTeacherProfileVO] = None):
        if profile is None and resume is None:
            raise ClientException(
                msg="at least one of the profile or resume is required")

        data = await self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}",
            json={
                "profile": None if profile is None else profile.dict(),
                "resume": resume.dict(),
            })

        return data

    async def enable_resume(self, host: str, teacher_id: int, resume_id: int, enable: bool):
        data = await self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}/enable/{enable}")

        return data

    async def delete_resume(self, host: str, teacher_id: int, resume_id: int):
        url = f"{host}/teachers/{teacher_id}/resumes/{resume_id}"
        data = await self.req.simple_delete(url=url)

        return data

    async def upsert_resume_section(self, host: str, resume_section: teach_vo.ResumeSectionVO):
        teacher_id = resume_section.tid
        resume_id = resume_section.rid
        data = await self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}/sections",
            json=resume_section.dict())

        return data
    
    async def delete_resume_section(self, host: str, teacher_id: int, resume_id: int, section_id: int):
        data = await self.req.simple_delete(
            url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}/sections/{section_id}")

        return data
