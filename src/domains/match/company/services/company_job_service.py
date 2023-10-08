from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....domains.match.company.value_objects import c_value_objects as com_vo
from .....configs.constants import BRIEF_JOB_SIZE
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class CompanyJobService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def create_job(self, host: str, register_region: str, company_id: int, job: com_vo.JobVO, profile: com_vo.UpdateCompanyProfileVO = None):
        job.published_in = register_region
        data = self.req.simple_post(
            url=f"{host}/companies/{company_id}/jobs",
            json={
                "profile": None if profile == None else profile.dict(),
                "job": job.dict(),
            })

        return data

    def get_brief_jobs(self, host: str, company_id: int, size: int, job_id: int = None):
        data = self.req.simple_get(
            url=f"{host}/companies/{company_id}/brief-jobs",
            params={
                "job_id": int(job_id) if job_id else None,
                "size": int(size) if size else BRIEF_JOB_SIZE,
            })
        # log.info(data)

        return data

    def get_job(self, host: str, company_id: int, job_id: int):
        data = self.req.simple_get(
            url=f"{host}/companies/{company_id}/jobs/{job_id}")

        return data

    def update_job(self, host: str, company_id: int, job_id: int, job: com_vo.UpdateJobVO = None, profile: com_vo.UpdateCompanyProfileVO = None):
        if profile == None and job == None:
            raise ClientException(
                msg="at least one of the profile or job is required")

        data = self.req.simple_put(
            url=f"{host}/companies/{company_id}/jobs/{job_id}",
            json={
                "profile": None if profile == None else profile.dict(),
                "job": job.dict(),
            })

        return data

    def enable_job(self, host: str, company_id: int, job_id: int, enable: bool):
        data = self.req.simple_put(
            url=f"{host}/companies/{company_id}/jobs/{job_id}/enable/{enable}")

        return data

    def delete_job(self, host: str, company_id: int, job_id: int):
        url = f"{host}/companies/{company_id}/jobs/{job_id}"
        data = self.req.simple_delete(url=url)

        return data
