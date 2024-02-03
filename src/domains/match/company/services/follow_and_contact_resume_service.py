from typing import Any, List, Dict, Optional
from ....cache import ICache
from ....service_api import IServiceApi
from ..value_objects import c_value_objects as com_vo
from ....notify.value_objects.email_value_objects import *
from ...star_tracker_service import StarTrackerService
from ....payment.services.payment_service import PaymentService
from ....payment.configs.constants import *
from .....configs.exceptions import *
from .....configs.constants import Apply
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class FollowResumeService(StarTrackerService):
    def __init__(self, req: IServiceApi, cache: ICache):
        super().__init__(req, cache)
        self.role = 'company'

    def upsert_follow_resume(self, host: str, company_id: int, resume_id: int, resume_info: com_vo.BaseResumeVO):
        data = self.req.simple_put(
            url=f"{host}/companies/{company_id}/follow/resumes/{resume_id}",
            json=resume_info.dict()
        )

        follow_resume = com_vo.FollowResumeVO.parse_obj(data)
        self.add_followed_star(self.role, company_id, follow_resume.rid)
        return follow_resume.init() # data

    def get_followed_resume_list(self, host: str, company_id: int, size: int, next_ts: int = None):
        data = self.req.simple_get(
            url=f"{host}/companies/{company_id}/follow/resumes",
            params={
                "size": size,
                "next_ts": next_ts,
            })

        followed_resume_list = com_vo.FollowResumeListVO.parse_obj(data)
        self.contact_marks(host, self.role, company_id, followed_resume_list.list)
        return followed_resume_list.init() # data

    def delete_followed_resume(self, host: str, company_id: int, resume_id: int) -> (bool):
        data = self.req.simple_delete(
            url=f"{host}/companies/{company_id}/follow/resumes/{resume_id}")

        self.remove_followed_star(self.role, company_id, resume_id)
        return data


class ContactResumeService(StarTrackerService):
    def __init__(self, req: IServiceApi, cache: ICache, payment_service: PaymentService):
        super().__init__(req, cache)
        self.role = 'company'
        self.payment_service = payment_service
        self.__cls_name = self.__class__.__name__

    def contact_teacher_by_email(self, auth_host: str, body: EmailVO):
        try:
            auth_email = EmailAuthVO.parse_obj(body)
            auth_email.sender_role = self.role
            auth_email.recipient_role = 'teacher'

            res = self.req.simple_post(
                url=f"{auth_host}/notify/email",
                json=auth_email.dict()
            )
            return res

        except Exception as e:
            log.error(f'{self.__cls_name}.contact_teacher_by_email error \n \
                auth_host:%s, body:%s, \n error:%s',
                auth_host, body, e.__str__())
            raise_http_exception(e)


    '''
    proactive: True
        the company need to pay
        
    proactive: False
        it's free to contact
    '''
    def __proactive(self, contact_resume: Optional[Dict]) -> (bool):
        proactive = True
        # need to pay, the company is trying to contact the teacher first
        if contact_resume is None:
            return proactive
        
        vo = com_vo.ContactResumeVO(**contact_resume)
        # its free to contact, because it's the teacher request
        if vo.my_status == Apply.PENDING:
            proactive = False
            
        return proactive
        
        

    def apply_resume(self, host: str, payment_host: str, company_id: int, body: com_vo.ApplyResumeVO):
        contact_resume = None
        payment_status = None
        data = None
        try:
            contact_resume = self.req.simple_get(
                url=f"{host}/companies/{company_id}/contact/resumes/{body.resume.rid}")
            
            if self.__proactive(contact_resume):
                payment_status = self.payment_service.get_payment_status(payment_host, company_id)
                if not payment_status.status in PAYMENT_PERIOD:
                    raise ClientException(msg='subscription_expired_or_not_exist')
                
            data = self.req.simple_put(
                url=f"{host}/companies/{company_id}/contact/resumes",
                json=body.fine_dict(),
            )
            contact_resume = com_vo.ContactResumeVO.parse_obj(data)
            self.add_contact_star(self.role, company_id, contact_resume.rid)
            return contact_resume.init() # data

        except Exception as e:
            log.error(f'{self.__cls_name}.apply_resume error \n \
                host:%s, payment_host:%s, company_id:%s, body:%s, \n \
                contact_resume:%s, payment_status:%s, apply_resume_result:%s, \n error:%s',
                host, payment_host, company_id, body, 
                contact_resume, payment_status, data, e.__str__())
            raise_http_exception(e, 'server_error')
            

    def get_any_contacted_resume_list(self, host: str, company_id: int, my_statuses: List[str], statuses: List[str], size: int, next_ts: int = None):
        data = self.req.simple_get(
            url=f"{host}/companies/{company_id}/contact/resumes",
            params={
                "my_statuses": my_statuses,
                "statuses": statuses,
                "size": size,
                "next_ts": next_ts
            })

        contact_resume_list = com_vo.ContactResumeListVO.parse_obj(data)
        self.followed_marks(host, self.role, company_id, contact_resume_list.list)
        return contact_resume_list.init() # data

    def delete_any_contacted_resume(self, host: str, company_id: int, resume_id: int) -> (bool):
        data = self.req.simple_delete(
            url=f"{host}/companies/{company_id}/contact/resumes/{resume_id}")

        self.remove_contact_star(self.role, company_id, resume_id)
        return data
