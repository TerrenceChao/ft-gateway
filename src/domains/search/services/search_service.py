from typing import Any, List, Dict
from ...service_api import IServiceApi
from ....configs.exceptions import *
from ....domains.search.value_objects import \
    c_value_objects as c, t_value_objects as t
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class SearchService:
    def __init__(self, req: IServiceApi):
        self.req = req
        self.__cls_name = self.__class__.__name__

    def get_resumes(self, search_host: str, query: t.SearchResumeListQueryDTO):
        url = f"{search_host}/resumes"
        data = self.req.simple_get(
            url=url,
            params=query.fine_dict(),
        )

        return t.SearchResumeListVO.parse_obj(data).init() # data

    '''
    TODO:
    - calculate the views
      - increse the count in cache
    - read [the resume] from match service
    '''
    def get_resume_by_id(self, match_host: str, teacher_id: int, resume_id: int):
        url = None
        data = None
        try:
            url = f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}"
            data = self.req.simple_get(url)
            return data
        except Exception as e:
            log.error(f"{self.__cls_name}.get_resume_by_id >> \
                url:{url}, response_data:{data}, error:{e}")
            raise_http_exception(e, 'teacher or resume not found')


    def get_jobs(self, search_host: str, query: c.SearchJobListQueryDTO):
        url = f"{search_host}/jobs"
        data = self.req.simple_get(
            url=url,
            params=query.fine_dict(),
        )

        return c.SearchJobListVO.parse_obj(data).init() # data

    '''
    TODO:
    - calculate the views
      - increse the count in cache
    - read [the job] from match service
    '''
    def get_job_by_id(self, match_host: str, company_id: int, job_id: int):
        url = None
        data = None
        try:
            url = f"{match_host}/companies/{company_id}/jobs/{job_id}"
            data = self.req.simple_get(url)
            return data
        except Exception as e:
            log.error(f"{self.__cls_name}.get_job_by_id >> \
                url:{url}, response_data:{data}, error:{e}")
            raise_http_exception(e, 'company or job not found')
