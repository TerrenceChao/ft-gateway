from typing import Any, List, Dict
from ...service_api import IServiceApi
from ....infra.db.nosql import match_teachers_schemas as schemas
from ....configs.exceptions import ClientException, \
    NotFoundException, \
    ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class TeacherService:
    def __init__(self, req: IServiceApi):
        self.req = req
        
    
    def get_profile(self, host: str, teacher_id: int):
        url=f"{host}/teachers/{teacher_id}"
        log.info(self.req)
        return self.req.get(url) # result, err


    def update_profile(self, host: str, teacher_id: int, profile: schemas.SoftTeacherProfile):
        url=f"{host}/teachers/{teacher_id}"
        return self.req.put(url=url, json=profile.dict()) # result, err


    def delete_resume(self, host: str, teacher_id: int, resume_id: int):
        url=f"{host}/teachers/{teacher_id}/resumes/{resume_id}"
        return self.req.delete(url=url) # result, err