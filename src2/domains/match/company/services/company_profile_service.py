from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....infra.db.nosql import match_companies_schemas as schemas
from .....configs.exceptions import ClientException, \
    NotFoundException, \
    ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class CompanyProfileService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def create_profile(self, host: str, profile: schemas.CompanyProfile):
        url = f"{host}/companies/"
        data, err = self.req.simple_post(url=url, json=profile.dict())
        if err:
            raise ServerException(msg=err)

        return data

    def get_profile(self, host: str, company_id: int):
        url = f"{host}/companies/{company_id}"
        data, err = self.req.simple_get(url)
        if err:
            raise ServerException(msg=err)

        return data

    def update_profile(self, host: str, company_id: int, profile: schemas.SoftCompanyProfile):
        url = f"{host}/companies/{company_id}"
        data, err = self.req.simple_put(url=url, json=profile.dict())
        if err:
            raise ServerException(msg=err)

        return data
