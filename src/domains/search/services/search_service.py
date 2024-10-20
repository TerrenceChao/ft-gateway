from typing import Any, List, Dict
from ...service_api import IServiceApi
from ...cache import ICache
from ....configs.exceptions import *
from ....configs.conf import SHORT_TERM_TTL
from ...match.company.value_objects import c_value_objects as match_c
from ...match.teacher.value_objects import t_value_objects as match_t
from ..value_objects import \
    c_value_objects as search_c, \
    t_value_objects as search_t, \
    public_value_objects as search_public
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


CONTINENTS = 'continents'
CONTINENT_ALL = 'continent-all'
CONTINENT_ = 'continent-'
RESUME_TAGS = 'resume-tags'


class SearchService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache

    async def get_resumes(self, search_host: str, query: search_t.SearchResumeListQueryDTO):
        url = f"{search_host}/resumes"
        data = await self.req.simple_get(
            url=url,
            params=query.fine_dict(),
        )

        return search_t.SearchResumeListVO.parse_obj(data).init()  # data

    '''
    TODO:
    - calculate the views
      - increse the count in cache
    - read [the resume] from match service
    '''

    async def get_resume_by_id(self, match_host: str, teacher_id: int, resume_id: int):
        url = None
        data = None
        try:
            url = f"{match_host}/teachers/{teacher_id}/resumes/{resume_id}"
            data = await self.__public_resume_vo(url)
            if await self.__resume_closed(data):
                return (None, 'resume closed')
            return (data, 'ok')

        except Exception as e:
            log.error(f"get_resume_by_id >> \
                url:{url}, response_data:{data}, error:{e}")
            raise ClientException(msg='teacher or resume not found')

    async def __public_resume_vo(self, url: str) -> (match_t.TeacherProfileAndResumeVO):
        resp = await self.req.simple_get(url)
        data = match_t.TeacherProfileAndResumeVO.parse_obj(resp)
        return data.public_info()

    async def __resume_closed(self, data: match_t.TeacherProfileAndResumeVO) -> (bool):
        return not data.resume or not data.resume.enable

    async def get_resume_tags(self, search_host: str) -> (search_public.ResumeTagsVO):
        data = await self.cache.get(RESUME_TAGS)
        if data is None:
            url = f'{search_host}/resumes-info/tags'
            data = await self.req.simple_get(url)
            await self.cache.set(RESUME_TAGS, data, SHORT_TERM_TTL)

        return data

    async def get_jobs(self, search_host: str, query: search_c.SearchJobListQueryDTO):
        url = f"{search_host}/jobs"
        data = await self.req.simple_get(
            url=url,
            params=query.fine_dict(),
        )

        return search_c.SearchJobListVO.parse_obj(data).init()  # data

    '''
    TODO:
    - calculate the views
      - increse the count in cache
    - read [the job] from match service
    '''

    async def get_job_by_id(self, match_host: str, company_id: int, job_id: int):
        url = None
        data = None
        try:
            url = f"{match_host}/companies/{company_id}/jobs/{job_id}"
            data = await self.__public_job_vo(url)
            if await self.__job_closed(data):
                return (None, 'job closed')
            return (data, 'ok')

        except Exception as e:
            log.error(f"get_job_by_id >> \
                url:{url}, response_data:{data}, error:{e}")
            raise ClientException(msg='company or job not found')

    async def __public_job_vo(self, url: str) -> (match_c.CompanyProfileAndJobVO):
        resp = await self.req.simple_get(url)
        data = match_c.CompanyProfileAndJobVO.parse_obj(resp)
        return data.public_info()

    async def __job_closed(self, data: match_c.CompanyProfileAndJobVO) -> (bool):
        return not data.job or not data.job.enable

    async def get_continents(self, search_host: str) -> (search_public.ContinentListVO):
        data = await self.cache.get(CONTINENTS)
        if data is None:
            url = f'{search_host}/jobs-info/continents'
            data = await self.req.simple_get(url)
            await self.cache.set(CONTINENTS, data, SHORT_TERM_TTL)

        return data

    async def get_all_continents_and_countries(self, search_host: str) -> (List[search_public.CountryListVO]):
        data = await self.cache.get(CONTINENT_ALL)
        if data is None:
            url = f'{search_host}/jobs-info/continents/all/countries'
            data = await self.req.simple_get(url)
            await self.cache.set(CONTINENT_ALL, data, SHORT_TERM_TTL)

        return data

    async def get_countries(self, search_host: str, continent_code: str) -> (List[search_public.CountryListVO]):
        data = await self.cache.get(f'{CONTINENT_}{continent_code}')
        if data is None:
            url = f'{search_host}/jobs-info/continents/{continent_code}/countries'
            data = await self.req.simple_get(url)
            await self.cache.set(
                f'{CONTINENT_}{continent_code}',
                data,
                SHORT_TERM_TTL
            )

        return data
