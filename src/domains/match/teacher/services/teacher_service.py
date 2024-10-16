from typing import Any, List, Dict, Optional
from ....service_api import IServiceApi
from ..value_objects import t_value_objects as teach_vo
from ...star_tracker_service import StarTrackerService
from ....cache import ICache
from .....configs.conf import \
    MY_STATUS_OF_TEACHER_APPLY, STATUS_OF_TEACHER_APPLY
from .....configs.exceptions import \
    ClientException, ServerException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class TeacherProfileService:
    def __init__(self, req: IServiceApi):
        self.req = req

    async def create_profile(self, host: str, teacher_id: int, profile: teach_vo.TeacherProfileVO):
        url = f"{host}/teachers/{teacher_id}"
        data = await self.req.simple_post(url=url, json=profile.dict())

        return data

    async def get_profile(self, host: str, teacher_id: int) -> (Optional[teach_vo.ReturnTeacherProfileVO]):
        return await TeacherProfileService.get(self.req, host, teacher_id)
    
    # public method for teacher & company:ContactResumeService
    @staticmethod
    async def get(req: IServiceApi, match_host: str, teacher_id: int) -> (Optional[teach_vo.ReturnTeacherProfileVO]):
        url = f"{match_host}/teachers/{teacher_id}"
        data = await req.simple_get(url)
        if data is None:
            return None

        return teach_vo.ReturnTeacherProfileVO.parse_obj(data)

    async def update_profile(self, host: str, teacher_id: int, profile: teach_vo.UpdateTeacherProfileVO):
        url = f"{host}/teachers/{teacher_id}"
        data = await self.req.simple_put(url=url, json=profile.dict())

        return data


class TeacherAggregateService(StarTrackerService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)

    async def get_job_follows_and_contacts(self, host: str, teacher_id: int, size: int):
        url = f"{host}/teachers/{teacher_id}/jobs/follow-and-apply"
        data = await self.req.simple_get(
            url=url, 
            params={
                "size": size,
                "my_statuses": MY_STATUS_OF_TEACHER_APPLY,
                "statuses": STATUS_OF_TEACHER_APPLY,
            }
        )

        data = teach_vo.TeacherFollowAndContactVO.parse_obj(data).init()
        data.followed = await self.contact_marks(host, 'teacher', teacher_id, data.followed)
        data.contact = await self.followed_marks(host, 'teacher', teacher_id, data.contact)
        return data

    async def get_matchdata(self, host: str, teacher_id: int, size: int):
        url = f"{host}/teachers/{teacher_id}/matchdata"
        data = await self.req.simple_get(
            url=url, 
            params={
                "size": size,
                "my_statuses": MY_STATUS_OF_TEACHER_APPLY,
                "statuses": STATUS_OF_TEACHER_APPLY,
            }
        )

        data = teach_vo.TeacherMatchDataVO.parse_obj(data).init()
        data.followed = await self.contact_marks(host, 'teacher', teacher_id, data.followed)
        data.contact = await self.followed_marks(host, 'teacher', teacher_id, data.contact)
        return data
