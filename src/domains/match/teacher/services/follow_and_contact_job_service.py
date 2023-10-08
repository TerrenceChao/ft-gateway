from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....domains.match.teacher.value_objects import t_value_objects as teach_vo
from .....configs.exceptions import \
    ClientException, ServerException
from .....configs.constants import Apply
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class FollowJobService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def upsert_follow_job(self, host: str, teacher_id: int, job_id: int, job_info: teach_vo.BaseJobVO):
        data = self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/follow/jobs/{job_id}",
            json=job_info.dict()
        )

        return data

    def get_followed_job_list(self, host: str, teacher_id: int, size: int, next_ts: int = None):
        data = self.req.simple_get(
            url=f"{host}/teachers/{teacher_id}/follow/jobs",
            params={
                "size": size,
                "next_ts": next_ts,
            })

        return data

    def delete_followed_job(self, host: str, teacher_id: int, job_id: int):
        data = self.req.simple_delete(
            url=f"{host}/teachers/{teacher_id}/follow/jobs/{job_id}")

        return data


class ContactJobService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def apply_job(self, host: str, teacher_id: int, body: teach_vo.ApplyJobVO):
        data = self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/contact/jobs",
            json=body.fine_dict()
        )

        return data

    def get_any_contacted_job_list(self, host: str, teacher_id: int, my_statuses: List[str], statuses: List[str], size: int, next_ts: int = None):
        data = self.req.simple_get(
            url=f"{host}/teachers/{teacher_id}/contact/jobs",
            params={
                "apply_statuses": my_statuses,
                # "statuses": statuses,
                "size": size,
                "next_ts": next_ts
            })

        return data

    def delete_any_contacted_job(self, host: str, teacher_id: int, job_id: int):
        data = self.req.simple_delete(
            url=f"{host}/teachers/{teacher_id}/contact/jobs/{job_id}")

        return data
