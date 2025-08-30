from typing import Any, List, Dict
from ....cache import ICache
from ....service_api import IServiceApi
from ..value_objects import t_value_objects as teach_vo
from ...star_tracker_service import StarTrackerService
from .....configs.exceptions import \
    ClientException, ServerException
from .....configs.constants import Apply
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class FollowJobService(StarTrackerService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)
        self.role = 'teacher'

    async def upsert_follow_job(self, host: str, teacher_id: int, job_id: int, job_info: teach_vo.BaseJobVO):
        data = await self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/follow/jobs/{job_id}",
            json=job_info.model_dump()
        )

        follow_job = teach_vo.FollowJobVO.model_validate(data)
        await self.add_followed_star(self.role, teacher_id, follow_job.jid)
        return follow_job.init() # data

    async def get_followed_job_list(self, host: str, teacher_id: int, size: int, next_ts: int = None):
        data = await self.req.simple_get(
            url=f"{host}/teachers/{teacher_id}/follow/jobs",
            params={
                "size": size,
                "next_ts": next_ts,
            })

        followed_job_list = teach_vo.FollowJobListVO.model_validate(data)
        await self.contact_marks(host, self.role, teacher_id, followed_job_list.list)
        return followed_job_list.init() # data

    async def delete_followed_job(self, host: str, teacher_id: int, job_id: int) -> bool:
        data = await self.req.simple_delete(
            url=f"{host}/teachers/{teacher_id}/follow/jobs/{job_id}")

        await self.remove_followed_star(self.role, teacher_id, job_id)
        return data


class ContactJobService(StarTrackerService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)
        self.role = 'teacher'

    async def apply_job(self, host: str, teacher_id: int, body: teach_vo.ApplyJobVO):
        data = await self.req.simple_put(
            url=f"{host}/teachers/{teacher_id}/contact/jobs",
            json=body.fine_dict()
        )

        contact_job = teach_vo.ContactJobVO.model_validate(data)
        await self.add_contact_star(self.role, teacher_id, contact_job.jid)
        return contact_job.init() # data

    async def get_any_contacted_job_list(self, host: str, teacher_id: int, my_statuses: List[str], statuses: List[str], size: int, next_ts: int = None):
        data = await self.req.simple_get(
            url=f"{host}/teachers/{teacher_id}/contact/jobs",
            params={
                "my_statuses": my_statuses,
                "statuses": statuses,
                "size": size,
                "next_ts": next_ts
            })

        contact_job_list = teach_vo.ContactJobListVO.model_validate(data)
        await self.followed_marks(host, self.role, teacher_id, contact_job_list.list)
        return contact_job_list.init() # data

    async def delete_any_contacted_job(self, host: str, teacher_id: int, job_id: int) -> bool:
        data = await self.req.simple_delete(
            url=f"{host}/teachers/{teacher_id}/contact/jobs/{job_id}")

        await self.remove_contact_star(self.role, teacher_id, job_id)
        return data
