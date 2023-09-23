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
            raise ServerException(msg=err)

        return data

    def get_job(self, host: str, company_id: int, job_id: int):
        data, err = self.req.simple_get(
            url=f"{host}/companies/{company_id}/jobs/{job_id}")
        if err:
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
            raise ServerException(msg=err)

        return data

    def enable_job(self, host: str, company_id: int, job_id: int, enable: bool):
        data, err = self.req.simple_put(
            url=f"{host}/companies/{company_id}/jobs/{job_id}/enable/{enable}")
        if err:
            raise ServerException(msg=err)

        return data

    def delete_job(self, host: str, company_id: int, job_id: int):
        url = f"{host}/companies/{company_id}/jobs/{job_id}"
        data, err = self.req.simple_delete(url=url)
        if err:
            raise ServerException(msg=err)

        return data