from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....domains.match.teacher.value_objects import t_value_objects as teach_vo
from .....configs.conf import \
    MY_STATUS_OF_TEACHER_APPLY, STATUS_OF_TEACHER_APPLY
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class TeacherProfileService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def create_profile(self, host: str, teacher_id: int, profile: teach_vo.TeacherProfileVO):
        url = f"{host}/teachers/{teacher_id}"
        data = self.req.simple_post(url=url, json=profile.dict())

        return data

    def get_profile(self, host: str, teacher_id: int):
        url = f"{host}/teachers/{teacher_id}"
        data = self.req.simple_get(url)

        return data

    def update_profile(self, host: str, teacher_id: int, profile: teach_vo.UpdateTeacherProfileVO):
        url = f"{host}/teachers/{teacher_id}"
        data = self.req.simple_put(url=url, json=profile.dict())

        return data


class TeacherAggregateService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def get_job_follows_and_contacts(self, host: str, teacher_id: int, size: int):
        url = f"{host}/teachers/{teacher_id}/jobs/follow-and-apply"
        data = self.req.simple_get(
            url=url, 
            params={
                "size": size,
                "my_statuses": MY_STATUS_OF_TEACHER_APPLY,
                "statuses": STATUS_OF_TEACHER_APPLY,
            }
        )

        return data

    def get_matchdata(self, host: str, teacher_id: int, size: int):
        url = f"{host}/teachers/{teacher_id}/matchdata"
        data = self.req.simple_get(
            url=url, 
            params={
                "size": size,
                "my_statuses": MY_STATUS_OF_TEACHER_APPLY,
                "statuses": STATUS_OF_TEACHER_APPLY,
            }
        )

        return data
