from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from ....configs.constants import *
from ....configs.conf import SEARCH_JOB_URL_PATH
from ...match.public_value_objects import MarkVO
from ....infra.db.nosql import match_companies_schemas as company


class SearchJobDTO(MarkVO):
    jid: Optional[int] = None
    cid: Optional[int] = None
    name: Optional[str] = None  # school/company/organization name
    logo: Optional[str] = None
    title:  Optional[str] = None  # job title
    continent_code: Optional[str] = None
    country_code: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    # job_desc: Optional[Dict] = None
    # others: Optional[Dict] = None
    tags: Optional[List[str]] = []
    views: Optional[int] = None
    updated_at: Optional[int] = None
    # created_at: Optional[int] = None
    region: Optional[str] = None  # must
    url_path: Optional[str] = None  # must

    def id(self) -> (int):
        return self.jid

    def init(self):
        if self.region and \
            self.cid and \
            self.jid:
            self.url_path = f'{SEARCH_JOB_URL_PATH}/{self.region}/{self.cid}/{self.jid}'

        return self


class SearchJobListVO(BaseModel):
    items: Optional[List[SearchJobDTO]] = []
    next: Optional[str] = None

    def init(self):
        [item.init() for item in self.items]
        return self


class SearchJobListQueryDTO(BaseModel):
    size: int
    sort_by: SortField = SortField.UPDATED_AT
    sort_dirction: SortDirection = SortDirection.DESC
    search_after: Optional[str] = None
    patterns: Optional[List[str]] = []
    continent_code: Optional[str] = None
    country_code: Optional[str] = None

    def fine_dict(self):
        dictionary = self.dict()
        dictionary['sort_by'] = self.sort_by.value
        dictionary['sort_dirction'] = self.sort_dirction.value
        return dictionary
