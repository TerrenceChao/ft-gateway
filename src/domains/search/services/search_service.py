from typing import Any, List, Dict
from ...service_api import IServiceApi
from ....configs.exceptions import *
from ....domains.match.company.value_objects import c_value_objects as match_c
from ....domains.match.teacher.value_objects import t_value_objects as match_t
from ....domains.search.value_objects import \
    c_value_objects as search_c, t_value_objects as search_t
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class SearchService:
    def __init__(self, req: IServiceApi):
        self.req = req
        self.__cls_name = self.__class__.__name__

    def get_resumes(self, search_host: str, query: search_t.SearchResumeListQueryDTO):
        url = f"{search_host}/resumes"
        data = self.req.simple_get(
            url=url,
            params=query.fine_dict(),
        )

        return search_t.SearchResumeListVO.parse_obj(data).init() # data

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
            if self.__resume_closed(data):
                return (None, 'resume closed')
            return (data, 'ok')

        except Exception as e:
            log.error(f"{self.__cls_name}.get_resume_by_id >> \
                url:{url}, response_data:{data}, error:{e}")
            raise ClientException(msg='teacher or resume not found')


    def __resume_closed(self, data: Dict) -> (bool):
        teacher_resume = match_t.TeacherProfileAndResumeVO.parse_obj(data)
        return not teacher_resume.resume or not teacher_resume.resume.enable


    def get_jobs(self, search_host: str, query: search_c.SearchJobListQueryDTO):
        url = f"{search_host}/jobs"
        data = self.req.simple_get(
            url=url,
            params=query.fine_dict(),
        )

        return search_c.SearchJobListVO.parse_obj(data).init() # data

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
            if self.__job_closed(data):
                return (None, 'job closed')
            return (data, 'ok')

        except Exception as e:
            log.error(f"{self.__cls_name}.get_job_by_id >> \
                url:{url}, response_data:{data}, error:{e}")
            raise ClientException(msg='company or job not found')


    def __job_closed(self, data: Dict) -> (bool):
        company_job = match_c.CompanyProfileAndJobVO.parse_obj(data)
        return not company_job.job or not company_job.job.enable
