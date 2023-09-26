from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....infra.db.nosql import match_companies_schemas as schemas
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class CompanyProfileService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def create_profile(self, host: str, profile: schemas.CompanyProfile):
        url = f"{host}/companies/"
        data, err = self.req.simple_post(url=url, json=profile.dict())
        if err:
            log.error(f"CompanyProfileService.create_profile fail: [request post], host:%s, profile:{{%s}}, data:%s, err:%s", host, profile, data, err)
            raise ServerException(msg=err)

        return data

    def get_profile(self, host: str, company_id: int):
        url = f"{host}/companies/{company_id}"
        data, err = self.req.simple_get(url)
        if err:
            log.error(f"CompanyProfileService.get_profile fail: [request get], host:%s, company_id:%s, data:%s, err:%s", host, company_id, data, err)
            raise ServerException(msg=err)

        return data

    def update_profile(self, host: str, company_id: int, profile: schemas.SoftCompanyProfile):
        url = f"{host}/companies/{company_id}"
        data, err = self.req.simple_put(url=url, json=profile.dict())
        if err:
            log.error(f"CompanyProfileService.update_profile fail: [request put], host:%s, company_id:%s, profile:{{%s}}, data:%s, err:%s", host, company_id, profile, data, err)
            raise ServerException(msg=err)

        return data
