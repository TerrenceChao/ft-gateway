from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....infra.db.nosql import match_teachers_schemas as schemas
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class TeacherResumeService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def create_resume(self, host: str, register_region: str, teacher_id: int, resume: schemas.Resume, profile: schemas.TeacherProfile = None):
        resume.published_in = register_region
        data, err = self.req.simple_post(
            url=f"{host}/teachers/{teacher_id}/resumes",
            json={
                "profile": None if profile == None else profile.dict(),
                "resume": resume.dict(),
            })
        if err:
            log.error(f"TeacherResumeService.create_resume fail: [request post], host:%s, teacher_id:%s, resume:{{%s}}, profile:{{%s}}, data:%s, err:%s", host, teacher_id, resume, profile, data, err)
            raise ServerException(msg=err)

        return data

    def get_brief_resumes(self, host: str, teacher_id: int):
        data, err = self.req.simple_get(
            url=f"{host}/teachers/{teacher_id}/resumes/brief")
        # log.info(data)
        if err:
            log.error(f"TeacherResumeService.get_brief_resumes fail: [request get], host:%s, teacher_id:%s, data:%s, err:%s", host, teacher_id, data, err)
            raise ServerException(msg=err)

        return data

    def get_resume(self, host: str, teacher_id: int, resume_id: int):
        data, err = self.req.simple_get(
            url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}")
        if err:
            log.error(f"TeacherResumeService.get_resume fail: [request get], host:%s, teacher_id:%s, resume_id:%s, data:%s, err:%s", host, teacher_id, resume_id, data, err)
            raise ServerException(msg=err)

        return data

    def update_resume(self, host: str, teacher_id: int, resume_id: int, resume: schemas.SoftResume = None, profile: schemas.SoftTeacherProfile = None):
        if profile == None and resume == None:
            raise ClientException(
                msg="at least one of the profile or resume is required")

        data, err = self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}",
            json={
                "profile": None if profile == None else profile.dict(),
                "resume": resume.dict(),
            })
        if err:
            log.error(f"TeacherResumeService.update_resume fail: [request put], host:%s, teacher_id:%s, resume_id:%s, resume:{{%s}}, profile:{{%s}}, data:%s, err:%s", host, teacher_id, resume_id, resume, profile, data, err)
            raise ServerException(msg=err)

        return data

    def enable_resume(self, host: str, teacher_id: int, resume_id: int, enable: bool):
        data, err = self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}/enable/{enable}")
        if err:
            log.error(f"TeacherResumeService.enable_resume fail: [request put], host:%s, teacher_id:%s, resume_id:%s, enable:%s, data:%s, err:%s", host, teacher_id, resume_id, enable, data, err)
            raise ServerException(msg=err)

        return data

    def delete_resume(self, host: str, teacher_id: int, resume_id: int):
        url = f"{host}/teachers/{teacher_id}/resumes/{resume_id}"
        data, err = self.req.simple_delete(url=url)
        if err:
            log.error(f"TeacherResumeService.delete_resume fail: [request delete], host:%s, teacher_id:%s, resume_id:%s, data:%s, err:%s", host, teacher_id, resume_id, data, err)
            raise ServerException(msg=err)

        return data
