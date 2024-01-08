from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from ....configs.constants import *
from ....infra.db.nosql import match_teachers_schemas as teacher


class BaseResumeVO(BaseModel):
    rid: Optional[int] = None
    tid: Optional[int] = None
    avator: Optional[str] = None
    fullname: Optional[str] = None
    intro: Optional[str] = None
    tags: Optional[List[str]] = []
    views: Optional[int] = None
    updated_at: Optional[int] = None
    created_at: Optional[int] = None
    published_in: Optional[str] = None  # must
    url_path: Optional[str] = None  # must


class ResumeListVO(BaseModel):
    items: Optional[List[BaseResumeVO]] = []
    next: Optional[str] = None


class SearchResumeListVO(BaseModel):
    size: int
    sort_by: SortField = SortField.UPDATED_AT
    sort_dirction: SortDirection = SortDirection.DESC
    search_after: Optional[int] = None


class SearchResumeDetailVO(teacher.Resume):
    fullname: Optional[str] = None
    avator: Optional[str] = None
    url_path: Optional[str] = None
    views: int = 0
