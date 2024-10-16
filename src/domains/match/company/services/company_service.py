from typing import Any, List, Dict
from ....service_api import IServiceApi
from ..value_objects import c_value_objects as com_vo
from ...star_tracker_service import StarTrackerService
from ....cache import ICache
from .....configs.conf import \
    MY_STATUS_OF_COMPANY_APPLY, STATUS_OF_COMPANY_APPLY
from .....configs.exceptions import \
    ClientException, ServerException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class CompanyProfileService:
    def __init__(self, req: IServiceApi):
        self.req = req

    async def create_profile(self, host: str, company_id: int, profile: com_vo.CompanyProfileVO):
        url = f"{host}/companies/{company_id}"
        data = await self.req.simple_post(url=url, json=profile.dict())
        
        return data

    async def get_profile(self, host: str, company_id: int):
        url = f"{host}/companies/{company_id}"
        data = await self.req.simple_get(url)

        return data

    async def update_profile(self, host: str, company_id: int, profile: com_vo.UpdateCompanyProfileVO):
        url = f"{host}/companies/{company_id}"
        data = await self.req.simple_put(url=url, json=profile.dict())

        return data


class CompanyAggregateService(StarTrackerService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)

    async def get_resume_follows_and_contacts(self, host: str, company_id: int, size: int):
        url = f"{host}/companies/{company_id}/resumes/follow-and-apply"
        data = await self.req.simple_get(
            url=url, 
            params={
                "size": size,
                "my_statuses": MY_STATUS_OF_COMPANY_APPLY,
                "statuses": STATUS_OF_COMPANY_APPLY,
            }
        )
        
        data = com_vo.CompanyFollowAndContactVO.parse_obj(data).init()
        data.followed = await self.contact_marks(host, 'company', company_id, data.followed)
        data.contact = await self.followed_marks(host, 'company', company_id, data.contact)
        return data

    async def get_matchdata(self, host: str, company_id: int, size: int):
        url = f"{host}/companies/{company_id}/matchdata"
        data = await self.req.simple_get(
            url=url, 
            params={
                "size": size,
                "my_statuses": MY_STATUS_OF_COMPANY_APPLY,
                "statuses": STATUS_OF_COMPANY_APPLY,
            }
        )
        
        data = com_vo.CompanyMatchDataVO.parse_obj(data).init()
        data.followed = await self.contact_marks(host, 'company', company_id, data.followed)
        data.contact = await self.followed_marks(host, 'company', company_id, data.contact)
        return data
