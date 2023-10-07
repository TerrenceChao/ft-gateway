from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....domains.match.company.value_objects import c_value_objects as com_vo
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class CompanyProfileService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def create_profile(self, host: str, company_id: int, profile: com_vo.CompanyProfileVO):
        url = f"{host}/companies/{company_id}"
        data, err = self.req.simple_post(url=url, json=profile.dict())
        if err:
            log.error(
                f"CompanyProfileService.create_profile fail: [request post], host:%s, profile:{{%s}}, data:%s, err:%s", host, profile, data, err)
            raise ServerException(msg=err)

        return data

    def get_profile(self, host: str, company_id: int):
        url = f"{host}/companies/{company_id}"
        data, err = self.req.simple_get(url)
        if err:
            log.error(
                f"CompanyProfileService.get_profile fail: [request get], host:%s, company_id:%s, data:%s, err:%s", host, company_id, data, err)
            raise ServerException(msg=err)

        return data

    def update_profile(self, host: str, company_id: int, profile: com_vo.UpdateCompanyProfileVO):
        url = f"{host}/companies/{company_id}"
        data, err = self.req.simple_put(url=url, json=profile.dict())
        if err:
            log.error(
                f"CompanyProfileService.update_profile fail: [request put], host:%s, company_id:%s, profile:{{%s}}, data:%s, err:%s", host, company_id, profile, data, err)
            raise ServerException(msg=err)

        return data


class CompanyAggregateService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def get_resume_follows_and_contacts(self, host: str, company_id: int, size: int):
        url = f"{host}/companies/{company_id}/resumes/follow-and-apply"
        data, err = self.req.simple_get_list(url=url, params={"size": size})
        if err:
            log.error(f"{self.__class__.__name__}.get_resume_follows_and_contacts fail: [request get],\
                host:%s, company_id:%s, size:%s, data:%s, err:%s",
                      host, company_id, size, data, err)
            raise ServerException(msg=err)

        return data

    def get_matchdata(self, host: str, company_id: int, size: int):
        url = f"{host}/companies/{company_id}/matchdata"
        data, err = self.req.simple_get_list(url=url, params={"size": size})
        if err:
            log.error(f"{self.__class__.__name__}.get_matchdata fail: [request get],\
                host:%s, company_id:%s, size:%s, data:%s, err:%s",
                      host, company_id, size, data, err)
            raise ServerException(msg=err)

        return data
