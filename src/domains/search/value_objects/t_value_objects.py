from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from ....configs.constants import *
from ....infra.db.nosql import match_teachers_schemas as teacher


class SearchResumeDTO(BaseModel):
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


class SearchResumeListVO(BaseModel):
    items: Optional[List[SearchResumeDTO]] = []
    next: Optional[str] = None


class SearchResumeListQueryDTO(BaseModel):
    size: int
    sort_by: SortField = SortField.UPDATED_AT
    sort_dirction: SortDirection = SortDirection.DESC
    search_after: Optional[str] = None

    def fine_dict(self):
        dictionary = self.dict()
        dictionary['sort_by'] = self.sort_by.value
        dictionary['sort_dirction'] = self.sort_dirction.value
        return dictionary

