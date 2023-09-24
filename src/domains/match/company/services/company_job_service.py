from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....infra.db.nosql import match_companies_schemas as schemas
from .....configs.constants import BRIEF_JOB_SIZE
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class CompanyJobService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def create_job(self, host: str, company_id: int, job: schemas.Job, profile: schemas.CompanyProfile = None):
        data, err = self.req.simple_post(
            url=f"{host}/companies/{company_id}/jobs",
            json={
                "profile": None if profile == None else profile.dict(),
                "job": job.dict(),
            })
        if err:
            log.error(f"CompanyJobService.create_job fail: [request post], host:%s, company_id:%s, job:{{%s}}, profile:{{%s}}, data:%s, err:%s", 
                      host, company_id, job, profile, data, err)
            raise ServerException(msg=err)

        return data

    def get_brief_jobs(self, host: str, company_id: int, job_id: int, size: int):
        data, err = self.req.simple_get_list(
            url=f"{host}/companies/{company_id}/jobs/brief",
            params={
                "job_id": int(job_id) if job_id else 0,
                "size": int(size) if size else BRIEF_JOB_SIZE,
            })
        # log.info(data)
        if err:
            log.error(f"CompanyJobService.get_brief_jobs fail: [request get list], host:%s, company_id:%s, job_id:%s, size:%s, data:%s, err:%s", 
                      host, company_id, job_id, size, data, err)
            raise ServerException(msg=err)

        return data

    def get_job(self, host: str, company_id: int, job_id: int):
        data, err = self.req.simple_get(
            url=f"{host}/companies/{company_id}/jobs/{job_id}")
        if err:
            log.error(f"CompanyJobService.get_job fail: [request get], host:%s, company_id:%s, job_id:%s, data:%s, err:%s", 
                      host, company_id, job_id, data, err)
            raise ServerException(msg=err)

        return data

    def update_job(self, host: str, company_id: int, job_id: int, job: schemas.SoftJob = None, profile: schemas.SoftCompanyProfile = None):
        if profile == None and job == None:
            raise ClientException(
                msg="at least one of the profile or job is required")

        data, err = self.req.simple_put(
            url=f"{host}/companies/{company_id}/jobs/{job_id}",
            json={
                "profile": None if profile == None else profile.dict(),
                "job": job.dict(),
            })
        if err:
            log.error(f"CompanyJobService.update_job fail: [request put], host:%s, company_id:%s, job_id:%s, job:{{%s}}, profile:{{%s}}, data:%s, err:%s", 
                      host, company_id, job_id, job, profile, data, err)
            raise ServerException(msg=err)

        return data

    def enable_job(self, host: str, company_id: int, job_id: int, enable: bool):
        data, err = self.req.simple_put(
            url=f"{host}/companies/{company_id}/jobs/{job_id}/enable/{enable}")
        if err:
            log.error(f"CompanyJobService.enable_job fail: [request put], host:%s, company_id:%s, job_id:%s, enable:%s, data:%s, err:%s", 
                      host, company_id, job_id, enable, data, err)
            raise ServerException(msg=err)

        return data

    def delete_job(self, host: str, company_id: int, job_id: int):
        url = f"{host}/companies/{company_id}/jobs/{job_id}"
        data, err = self.req.simple_delete(url=url)
        if err:
            log.error(f"CompanyJobService.delete_job fail: [request delete], host:%s, company_id:%s, job_id:%s, data:%s, err:%s", 
                      host, company_id, job_id, data, err)
            raise ServerException(msg=err)

        return data
