from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....domains.match.teacher.value_objects import t_value_objects as teach_vo
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class FollowJobService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def upsert_follow_job(self, host: str, teacher_id: int, job_id: int, job_info: teach_vo.BaseJobVO):
        data, err = self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/follow/jobs/{job_id}",
            json=job_info.dict()
        )
        if err:
            log.error(
                f"{self.__class__.__name__}.upsert_follow_job fail: [request post],\
                    host:%s, teacher_id:%s, job_id:%s, job_info:%s, data:%s, err:%s", 
                    host, teacher_id, job_id, job_info, data, err)
            raise ServerException(msg=err)

        return data

    def get_followed_job_list(self, host: str, teacher_id: int, size: int, next_ts: int = None):
        data, err = self.req.simple_get_list(
            url=f"{host}/teachers/{teacher_id}/follow/jobs",
            params={
                "size": size,
                "next_ts": next_ts,
            })

        if err:
            log.error(f"{self.__class__.__name__}.get_followed_job_list fail: [request get],\
                host:%s, teacher_id:%s, size:%s, next_ts:%s, data:%s, err:%s",
                      host, teacher_id, size, next_ts, data, err)
            raise ServerException(msg=err)

        return data

    def delete_followed_job(self, host: str, teacher_id: int, job_id: int):
        data, err = self.req.simple_delete(
            url=f"{host}/teachers/{teacher_id}/follow/jobs/{job_id}")
        if err:
            log.error(f"{self.__class__.__name__}.delete_followed_job fail: [request post],\
                host:%s, teacher_id:%s, data:%s, err:%s",
                      host, teacher_id, data, err)
            raise ServerException(msg=err)

        return data
