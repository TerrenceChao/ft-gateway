from typing import Any, List, Dict
from ...service_api import IServiceApi
from ....domains.search.value_objects import \
    c_value_objects as c, t_value_objects as t
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class SearchService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def get_resumes(self, search_host: str, query: t.SearchResumeListVO):
        url = f"{search_host}/resumes"
        data = self.req.simple_get(
            url=url,
            params=query.fine_dict(),
        )

        return data

    '''
    - calculate the views
      - increse the count in cache
    - read [the resume] from match service
    '''
    def get_resume_by_id(self, match_host: str, teacher_id: int, resume_id: int):
        url = f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}"
        data = self.req.simple_get(url)
        return data

    def get_jobs(self, search_host: str, query: c.SearchJobListVO):
        url = f"{search_host}/jobs"
        data = self.req.simple_get(
            url=url,
            params=query.fine_dict(),
        )

        return data

    '''
    - calculate the views
      - increse the count in cache
    - read [the job] from match service
    '''
    def get_job_by_id(self, match_host: str, company_id: int, job_id: int):
        url = f"{match_host}/companies/{company_id}/jobs/{job_id}"
        data = self.req.simple_get(url)
        return data
