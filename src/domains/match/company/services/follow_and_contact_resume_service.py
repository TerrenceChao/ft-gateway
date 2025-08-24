from typing import Any, List, Dict, Optional
from ....cache import ICache
from ....service_api import IServiceApi
from ..value_objects import c_value_objects as com_vo
from ....notify.value_objects.email_value_objects import *
from ...star_tracker_service import StarTrackerService
from ....payment.configs.constants import *
from .....configs.exceptions import *
from .....configs.constants import Apply
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class FollowResumeService(StarTrackerService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)
        self.role = 'company'

    async def upsert_follow_resume(self, host: str, company_id: int, resume_id: int, resume_info: com_vo.BaseResumeVO):
        data = await self.req.simple_put(
            url=f"{host}/companies/{company_id}/follow/resumes/{resume_id}",
            json=resume_info.model_dump()
        )

        follow_resume = com_vo.FollowResumeVO.model_validate(data)
        await self.add_followed_star(self.role, company_id, follow_resume.rid)
        return follow_resume.init() # data

    async def get_followed_resume_list(self, host: str, company_id: int, size: int, next_ts: int = None):
        data = await self.req.simple_get(
            url=f"{host}/companies/{company_id}/follow/resumes",
            params={
                "size": size,
                "next_ts": next_ts,
            })

        followed_resume_list = com_vo.FollowResumeListVO.model_validate(data)
        await self.contact_marks(host, self.role, company_id, followed_resume_list.list)
        return followed_resume_list.init() # data

    async def delete_followed_resume(self, host: str, company_id: int, resume_id: int) -> bool:
        data = await self.req.simple_delete(
            url=f"{host}/companies/{company_id}/follow/resumes/{resume_id}")

        await self.remove_followed_star(self.role, company_id, resume_id)
        return data


class ContactResumeService(StarTrackerService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)
        self.role = 'company'
        self.__cls_name = self.__class__.__name__

    async def contact_teacher_by_email(self, auth_host: str, body: EmailVO, teacher_profile_email: str = None):
        try:
            auth_email = EmailAuthVO.model_validate(body)
            auth_email.sender_role = self.role
            auth_email.recipient_role = 'teacher'
            auth_email.recipient_email = teacher_profile_email

            res = await self.req.simple_post(
                url=f"{auth_host}/notify/email",
                json=auth_email.model_dump()
            )
            return res

        except Exception as e:
            log.error(f'{self.__cls_name}.contact_teacher_by_email error \n \
                auth_host:%s, body:%s, teacher_profile_email:%s, \n error:%s',
                auth_host, body, teacher_profile_email, e.__str__())
            raise_http_exception(e)


    '''
    proactive: True
        the company need to pay
        
    proactive: False
        it's free to contact
    '''
    @staticmethod
    def is_proactive(contact_resume: Optional[com_vo.ContactResumeVO]) -> bool:
        proactive = True
        # need to pay, the company is trying to contact the teacher first
        if contact_resume is None:
            return proactive
        
        # its free to contact, because it's the teacher request
        if contact_resume.my_status == Apply.PENDING:
            proactive = False
            
        return proactive


    async def get_contact_resume(self, host: str, company_id: int, resume_id: int) -> Optional[com_vo.ContactResumeVO]:
        url=f"{host}/companies/{company_id}/contact/resumes/{resume_id}"
        contact_resume = await self.req.simple_get(url=url)
        if contact_resume is None:
            return None
        
        return com_vo.ContactResumeVO.model_validate(contact_resume)

    async def is_proactive_require(self, host: str, company_id: int, resume_id: int) -> bool:
        # if not contact yet, it's proactive
        contact_id_set = await self.contact_id_set(host, self.role, company_id)
        if not resume_id in contact_id_set:
            return True

        contact_resume = \
            await self.get_contact_resume(
                host,
                company_id,
                resume_id
            )
        return self.is_proactive(contact_resume)


    async def apply_resume(self, host: str, company_id: int, body: com_vo.ApplyResumeVO):
        data = await self.req.simple_put(
            url=f"{host}/companies/{company_id}/contact/resumes",
            json=body.fine_dict(),
        )

        contact_resume = com_vo.ContactResumeVO.model_validate(data)
        await self.add_contact_star(self.role, company_id, contact_resume.rid)
        return contact_resume.init() # data

    async def get_any_contacted_resume_list(self, host: str, company_id: int, my_statuses: List[str], statuses: List[str], size: int, next_ts: int = None):
        data = await self.req.simple_get(
            url=f"{host}/companies/{company_id}/contact/resumes",
            params={
                "my_statuses": my_statuses,
                "statuses": statuses,
                "size": size,
                "next_ts": next_ts
            })

        contact_resume_list = com_vo.ContactResumeListVO.model_validate(data)
        await self.followed_marks(host, self.role, company_id, contact_resume_list.list)
        return contact_resume_list.init() # data

    async def delete_any_contacted_resume(self, host: str, company_id: int, resume_id: int) -> bool:
        data = await self.req.simple_delete(
            url=f"{host}/companies/{company_id}/contact/resumes/{resume_id}")

        await self.remove_contact_star(self.role, company_id, resume_id)
        return data
