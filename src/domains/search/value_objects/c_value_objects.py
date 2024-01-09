from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from ....configs.constants import *
from ....configs.conf import SEARCH_JOB_URL_PATH
from ....infra.db.nosql import match_companies_schemas as company


class SearchJobDTO(BaseModel):
    jid: Optional[int] = None
    cid: Optional[int] = None
    name: Optional[str] = None  # school/company/organization name
    logo: Optional[str] = None
    title:  Optional[str] = None  # job title
    region: Optional[str] = None
    salary: Optional[str] = None
    # job_desc: Optional[Dict] = None
    # others: Optional[Dict] = None
    tags: Optional[List[str]] = []
    views: Optional[int] = None
    updated_at: Optional[int] = None
    # created_at: Optional[int] = None
    published_in: Optional[str] = None  # must
    url_path: Optional[str] = None  # must
    
    def init(self):
        if self.published_in and \
            self.cid and \
            self.jid:
            self.url_path = f'{SEARCH_JOB_URL_PATH}/{self.published_in}/{self.cid}/{self.jid}'
        
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
    
    def fine_dict(self):
        dictionary = self.dict()
        dictionary['sort_by'] = self.sort_by.value
        dictionary['sort_dirction'] = self.sort_dirction.value
        return dictionary

