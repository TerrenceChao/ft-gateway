from typing import Any, List, Dict
from ...service_api import IServiceApi
from ....infra.db.nosql import match_companies_schemas as schemas
from ....configs.exceptions import ClientException, \
    NotFoundException, \
    ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class CompanyService:
    def __init__(self, req: IServiceApi):
        self.req = req
        
    
    def get_profile(self, host: str, company_id: int):
        url=f"{host}/companies/{company_id}"
        return self.req.get(url) # data, err
    
    
    def update_profile(self, host: str, company_id: int, profile: schemas.SoftCompanyProfile):
        url=f"{host}/companies/{company_id}"
        return self.req.put(url=url, json=profile.dict()) # data, err
    
    
    def delete_job(self, host: str, company_id: int, job_id: int):
        url=f"{host}/companies/{company_id}/jobs/{job_id}"
        return self.req.delete(url=url) # data, err