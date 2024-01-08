from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from ....configs.constants import *
from ....infra.db.nosql import match_companies_schemas as company


class BaseJobVO(BaseModel):
    jid: Optional[int] = None
    cid: Optional[int] = None
    name: Optional[str] = None  # school/company/organization name
    logo: Optional[str] = None
    title:  Optional[str] = None  # job title
    region: Optional[str] = None
    salary: Optional[str] = None
    job_desc: Optional[Dict] = None
    others: Optional[Dict] = None
    tags: Optional[List[str]] = []
    views: Optional[int] = None
    updated_at: Optional[int] = None
    created_at: Optional[int] = None
    published_in: Optional[str] = None  # must
    url_path: Optional[str] = None  # must


class JobListVO(BaseModel):
    items: Optional[List[BaseJobVO]] = []
    next: Optional[str] = None


class SearchJobListVO(BaseModel):
    size: int
    sort_by: SortField = SortField.UPDATED_AT
    sort_dirction: SortDirection = SortDirection.DESC
    search_after: Optional[str] = None
    
    def fine_dict(self):
        dictionary = self.dict()
        dictionary['sort_by'] = self.sort_by.value
        dictionary['sort_dirction'] = self.sort_dirction.value
        return dictionary


class SearchJobDetailVO(company.Job, company.CompanyProfile):
    url_path: Optional[str] = None
    views: int = 0
