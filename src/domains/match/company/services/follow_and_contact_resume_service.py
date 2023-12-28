from typing import Any, List, Dict, Optional
from ....service_api import IServiceApi
from .....domains.match.company.value_objects import c_value_objects as com_vo
from .....domains.payment.services.payment_service import PaymentService
from .....domains.payment.configs.constants import *
from .....configs.exceptions import *
from .....configs.constants import Apply
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class FollowResumeService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def upsert_follow_resume(self, host: str, company_id: int, resume_id: int, resume_info: com_vo.BaseResumeVO):
        data = self.req.simple_put(
            url=f"{host}/companies/{company_id}/follow/resumes/{resume_id}",
            json=resume_info.dict()
        )

        return data

    def get_followed_resume_list(self, host: str, company_id: int, size: int, next_ts: int = None):
        data = self.req.simple_get(
            url=f"{host}/companies/{company_id}/follow/resumes",
            params={
                "size": size,
                "next_ts": next_ts,
            })

        return data

    def delete_followed_resume(self, host: str, company_id: int, resume_id: int):
        data = self.req.simple_delete(
            url=f"{host}/companies/{company_id}/follow/resumes/{resume_id}")

        return data


class ContactResumeService:
    def __init__(self, req: IServiceApi, payment_service: PaymentService):
        self.req = req
        self.payment_service = payment_service
        self.__cls_name = self.__class__.__name__
        
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
                if not payment_status['status'] in PAYMENT_PERIOD:
                    raise ClientException(msg='subscription_expired_or_not_exist')
                
            data = self.req.simple_put(
                url=f"{host}/companies/{company_id}/contact/resumes",
                json=body.fine_dict(),
            )
            return data

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

        return data

    def delete_any_contacted_resume(self, host: str, company_id: int, resume_id: int):
        data = self.req.simple_delete(
            url=f"{host}/companies/{company_id}/contact/resumes/{resume_id}")

        return data
