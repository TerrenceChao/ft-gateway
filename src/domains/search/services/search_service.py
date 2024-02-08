from typing import Any, List, Dict
from ...service_api import IServiceApi
from ....configs.exceptions import *
from ...match.company.value_objects import c_value_objects as match_c
from ...match.teacher.value_objects import t_value_objects as match_t
from ..value_objects import \
    c_value_objects as search_c, \
    t_value_objects as search_t, \
    public_value_objects as search_public
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
            data = self.__public_resume_vo(url)
            if self.__resume_closed(data):
                return (None, 'resume closed')
            return (data, 'ok')

        except Exception as e:
            log.error(f"{self.__cls_name}.get_resume_by_id >> \
                url:{url}, response_data:{data}, error:{e}")
            raise ClientException(msg='teacher or resume not found')

    def __public_resume_vo(self, url: str) -> (match_t.TeacherProfileAndResumeVO):
        resp = self.req.simple_get(url)
        data = match_t.TeacherProfileAndResumeVO.parse_obj(resp)
        return data.public_info()

    def __resume_closed(self, data: match_t.TeacherProfileAndResumeVO) -> (bool):
        return not data.resume or not data.resume.enable

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
            data = self.__public_job_vo(url)
            if self.__job_closed(data):
                return (None, 'job closed')
            return (data, 'ok')

        except Exception as e:
            log.error(f"{self.__cls_name}.get_job_by_id >> \
                url:{url}, response_data:{data}, error:{e}")
            raise ClientException(msg='company or job not found')

    def __public_job_vo(self, url: str) -> (match_c.CompanyProfileAndJobVO):
        resp = self.req.simple_get(url)
        data = match_c.CompanyProfileAndJobVO.parse_obj(resp)
        return data.public_info()

    def __job_closed(self, data: match_c.CompanyProfileAndJobVO) -> (bool):
        return not data.job or not data.job.enable

    def get_continents(self, search_host: str) -> (search_public.ContinentListVO):
        url = f'{search_host}/jobs-info/continents'
        data = self.req.simple_get(url)
        return data

    def get_countries(self, search_host: str, continent_code: str) -> (search_public.CountryListVO):
        url = f'{search_host}/jobs-info/continents/{continent_code}/countries'
        data = self.req.simple_get(url)
        return data
