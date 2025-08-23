from typing import Any, List, Dict, Optional
from ....service_api import IServiceApi
from .....domains.match.company.value_objects import c_value_objects as com_vo
from .....configs.constants import BRIEF_JOB_SIZE
from .....configs.exceptions import \
    ClientException, ServerException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class CompanyJobService:
    def __init__(self, req: IServiceApi):
        self.req = req

    async def create_job(self, host: str, register_region: str, company_id: int, job: com_vo.JobVO, profile: Optional[com_vo.UpdateCompanyProfileVO] = None):
        job.region = register_region
        data = await self.req.simple_post(
            url=f"{host}/companies/{company_id}/jobs",
            json={
                "profile": None if profile == None else profile.model_dump(),
                "job": job.model_dump(),
            })

        return data

    async def get_brief_jobs(self, host: str, company_id: int, size: int, job_id: int = None):
        data = await self.req.simple_get(
            url=f"{host}/companies/{company_id}/brief-jobs",
            params={
                "job_id": int(job_id) if job_id else None,
                "size": int(size) if size else BRIEF_JOB_SIZE,
            })
        # log.info(data)

        return data

    async def get_job(self, host: str, company_id: int, job_id: int):
        data = await self.req.simple_get(
            url=f"{host}/companies/{company_id}/jobs/{job_id}")

        return data

    async def update_job(self, host: str, company_id: int, job_id: int, job: Optional[com_vo.UpdateJobVO] = None, profile: Optional[com_vo.UpdateCompanyProfileVO] = None):
        if profile == None and job == None:
            raise ClientException(
                msg="at least one of the profile or job is required")

        data = await self.req.simple_put(
            url=f"{host}/companies/{company_id}/jobs/{job_id}",
            json={
                "profile": None if profile == None else profile.model_dump(),
                "job": job.model_dump(),
            })

        return data

    async def enable_job(self, host: str, company_id: int, job_id: int, enable: bool):
        data = await self.req.simple_put(
            url=f"{host}/companies/{company_id}/jobs/{job_id}/enable/{enable}")

        return data

    async def delete_job(self, host: str, company_id: int, job_id: int):
        url = f"{host}/companies/{company_id}/jobs/{job_id}"
        data = await self.req.simple_delete(url=url)

        return data
