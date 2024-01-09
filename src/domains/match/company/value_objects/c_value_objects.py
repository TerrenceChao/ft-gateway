from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from .....infra.db.nosql import match_companies_schemas as company
from .....infra.db.nosql import match_teachers_schemas as teacher
from ...public_value_objects import JobIndexVO, BaseResumeVO
from .....configs.constants import Apply
from .....configs.conf import SEARCH_RESUME_URL_PATH


class _BaseResumeData(BaseModel):
    url_path: Optional[str] = None
    
    def init(self):
        if self.resume_info != None:
            resume = self.resume_info
            self.url_path = f'{SEARCH_RESUME_URL_PATH}/{resume.published_in}/{resume.tid}/{resume.rid}'
        return self


class ContactResumeVO(_BaseResumeData):
    rid: int
    cid: int
    jid: int  # NOT ForeignKey
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    resume_info: Optional[Dict] = None
    created_at: Optional[int] = None


class ContactResumeListVO(BaseModel):
    list: List[ContactResumeVO] = []
    next_ts: Optional[int] = None
    
    def init(self):
        [item.init() for item in self.list]
        return self


class FollowResumeVO(_BaseResumeData):
    rid: int
    cid: int
    resume_info: BaseResumeVO
    created_at: Optional[int] = None


class FollowResumeListVO(BaseModel):
    list: List[FollowResumeVO] = []
    next_ts: Optional[int] = None
    
    def init(self):
        [item.init() for item in self.list]
        return self


class JobVO(BaseModel):
    # jid: Optional[int] = None
    # cid: int
    title: str
    region: str
    salary: str
    job_desc: Optional[Dict] = None
    # extra data, photos
    others: Optional[Dict] = None
    tags: Optional[List[str]] = []
    enable: bool = True
    # it's optional in gateway
    published_in: str


class UpdateJobVO(BaseModel):
    # jid: Optional[int] = None
    # cid: int
    title: Optional[str] = None
    region: Optional[str] = None
    salary: Optional[str] = None
    job_desc: Optional[Dict] = None
    # extra data, photos
    others: Optional[Dict] = None
    tags: Optional[List[str]] = []
    enable: Optional[bool] = True


class ReturnJobVO(UpdateJobVO):
    jid: Optional[int] = None
    cid: int
    # it's optional in gateway
    published_in: str


class JobListVO(BaseModel):
    list: List[ReturnJobVO] = []
    next_jid: Optional[int] = None


class EnableJobVO(BaseModel):
    jid: int
    cid: int
    enable: bool


class CompanyProfileVO(BaseModel):
    # cid: int
    name: str
    intro: str
    logo: Optional[str] = None
    # size, founded, revenue, ... etc (json)
    overview: Optional[Dict] = None
    # who, what, where, ... etc (json array)
    sections: Optional[List[Dict]] = []
    photos: Optional[List[Dict]] = []


class UpdateCompanyProfileVO(BaseModel):
    # cid: int
    name: Optional[str] = None
    intro: Optional[str] = None
    logo: Optional[str] = None
    # size, founded, revenue, ... etc (json)
    overview: Optional[Dict] = None
    # who, what, where, ... etc (json array)
    sections: Optional[List[Dict]] = []
    photos: Optional[List[Dict]] = []


class ReturnCompanyProfileVO(UpdateCompanyProfileVO):
    cid: int


class CompanyVO(CompanyProfileVO):
    brief_jobs: Optional[List[ReturnJobVO]] = []
    followed: Optional[List[FollowResumeVO]] = []
    contact: Optional[List[ContactResumeVO]] = []


class CompanyMatchDataVO(BaseModel):
    brief_jobs: Optional[List[ReturnJobVO]] = []
    followed: Optional[List[FollowResumeVO]] = []
    contact: Optional[List[ContactResumeVO]] = []


class CompanyFollowAndContactVO(BaseModel):
    followed: Optional[List[FollowResumeVO]] = []
    contact: Optional[List[ContactResumeVO]] = []


class ApplyResumeVO(BaseModel):
    # register_region: Optional[str] = None
    current_region: Optional[str] = None
    my_status: Apply
    # status: Optional[Apply] = Apply.PENDING
    resume: BaseResumeVO
    job_info: JobIndexVO

    def fine_dict(self):
        dictionary = self.dict()
        dictionary["my_status"] = self.my_status.value
        return dictionary


class CompanyProfileAndJobVO(BaseModel):
    profile: ReturnCompanyProfileVO
    # for search API, need created/updated/last_updated time
    job: Optional[company.Job] = None
