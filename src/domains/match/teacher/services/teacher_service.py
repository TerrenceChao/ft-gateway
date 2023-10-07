from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....domains.match.teacher.value_objects import t_value_objects as teach_vo
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class TeacherProfileService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def create_profile(self, host: str, teacher_id: int, profile: teach_vo.TeacherProfileVO):
        url = f"{host}/teachers/{teacher_id}"
        data, err = self.req.simple_post(url=url, json=profile.dict())
        if err:
            log.error(
                f"TeacherProfileService.create_profile fail: [request post], host:%s, profile:{{%s}}, data:%s, err:%s", host, profile, data, err)
            raise ServerException(msg=err)

        return data

    def get_profile(self, host: str, teacher_id: int):
        url = f"{host}/teachers/{teacher_id}"
        data, err = self.req.simple_get(url)
        if err:
            log.error(
                f"TeacherProfileService.get_profile fail: [request get], host:%s, teacher_id:%s, data:%s, err:%s", host, teacher_id, data, err)
            raise ServerException(msg=err)

        return data

    def update_profile(self, host: str, teacher_id: int, profile: teach_vo.UpdateTeacherProfileVO):
        url = f"{host}/teachers/{teacher_id}"
        data, err = self.req.simple_put(url=url, json=profile.dict())
        if err:
            log.error(
                f"TeacherProfileService.update_profile fail: [request put], host:%s, teacher_id:%s, profile:{{%s}}, data:%s, err:%s", host, teacher_id, profile, data, err)
            raise ServerException(msg=err)

        return data


class TeacherAggregateService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def get_job_follows_and_contacts(self, host: str, teacher_id: int, size: int):
        url = f"{host}/teachers/{teacher_id}/jobs/follow-and-apply"
        data, err = self.req.simple_get_list(url=url, params={"size": size})
        if err:
            log.error(f"{self.__class__.__name__}.get_job_follows_and_contacts fail: [request get],\
                host:%s, teacher_id:%s, size:%s, data:%s, err:%s",
                      host, teacher_id, size, data, err)
            raise ServerException(msg=err)

        return data

    def get_matchdata(self, host: str, teacher_id: int, size: int):
        url = f"{host}/teachers/{teacher_id}/matchdata"
        data, err = self.req.simple_get_list(url=url, params={"size": size})
        if err:
            log.error(f"{self.__class__.__name__}.get_matchdata fail: [request get],\
                host:%s, teacher_id:%s, size:%s, data:%s, err:%s",
                      host, teacher_id, size, data, err)
            raise ServerException(msg=err)

        return data
