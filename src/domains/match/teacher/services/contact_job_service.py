from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....domains.match.teacher.value_objects import t_value_objects as teach_vo
from .....configs.constants import Apply
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class ContactJobService:
    def __init__(self, req: IServiceApi):
        self.req = req
        
    def apply_job(self, host: str, teacher_id: int, body: teach_vo.ApplyJobVO):
        data, err = self.req.simple_put(
            url = f"{host}/teachers/{teacher_id}/contact/jobs",
            json=body.fine_dict()
        )
        if err:
            log.error(
                f"{self.__class__.__name__}.apply_job fail: [request post],\
                    host:%s, teacher_id:%s, body:%s, data:%s, err:%s",
                host, teacher_id, body, data, err)
            raise ServerException(msg=err)

        return data
    
    def get_any_contacted_job_list(self, host: str, teacher_id: int, my_statuses: List[Apply], statuses: List[Apply], size: int, next_ts: int = None):
        data, err = self.req.simple_get_list(
            url = f"{host}/teachers/{teacher_id}/contact/jobs",
            params={
                "my_statuses": my_statuses,
                "statuses": statuses,
                "size": size,
                "next_ts": next_ts
            })
        if err:
            log.error(
                f"{self.__class__.__name__}.get_any_contacted_job_list fail: [request get],\
                    host:%s, teacher_id:%s, my_statuses:%s, statuses:%s, size:%s, next_ts:%s, data:%s, err:%s",
                host, teacher_id, my_statuses, statuses, size, next_ts, data, err)
            raise ServerException(msg=err)

        return data
    
    
    def delete_any_contacted_job(self, host: str, teacher_id: int, job_id: int):
        data, err = self.req.simple_delete(
            url = f"{host}/teachers/{teacher_id}/contact/jobs/{job_id}")
        if err:
            log.error(
                f"{self.__class__.__name__}.delete_any_contacted_job fail: [request get],\
                    host:%s, teacher_id:%s, job_id:%s, data:%s, err:%s",
                host, teacher_id, job_id, data, err)
            raise ServerException(msg=err)

        return data