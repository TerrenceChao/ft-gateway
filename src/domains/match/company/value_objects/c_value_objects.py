from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from .....infra.db.nosql import match_companies_schemas as company
from .....infra.db.nosql import match_teachers_schemas as teacher
from ...public_value_objects import JobIndexVO, BaseResumeVO
from .....configs.constants import Apply


class ContactResumeVO(BaseModel):
    rid: int
    cid: int
    jid: int  # NOT ForeignKey
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    resume_info: Optional[Dict] = None
    created_at: Optional[int] = None


class FollowResumeVO(BaseModel):
    rid: int
    cid: int
    resume_info: BaseResumeVO
    created_at: Optional[int] = None


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
    published_in: Optional[str] = None

    def model(self, company_id: int):
        return company.Job(
            # jid=self.jid,
            cid=company_id,
            title=self.title,
            region=self.region,
            salary=self.salary,
            job_desc=self.job_desc,
            others=self.others,
            tags=self.tags,
            enable=self.enable,
            published_in=self.published_in,
        )


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

    def model(self, company_id: int, job_id: int):
        return company.Job(
            jid=job_id,
            cid=company_id,
            title=self.title,
            region=self.region,
            salary=self.salary,
            job_desc=self.job_desc,
            others=self.others,
            tags=self.tags,
            enable=self.enable,
        )


class ReturnJobVO(UpdateJobVO):
    jid: Optional[int] = None
    cid: int


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

    def model(self, company_id: int):
        return company.CompanyProfile(
            cid=company_id,
            name=self.name,
            intro=self.intro,
            logo=self.logo,
            overview=self.overview,
            sections=self.sections,
            photos=self.photos,
        )


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

    def model(self, company_id: int):
        return company.CompanyProfile(
            cid=company_id,
            name=self.name,
            intro=self.intro,
            logo=self.logo,
            overview=self.overview,
            sections=self.sections,
            photos=self.photos,
        )


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

    # TODO: resume 需要 hash code + 驗證，防竄改
    # resume 是從外部傳入，不須在內部查找 DB
    def gen_contact_resume(self, cid: int):
        return company.ContactResume(
            rid=self.resume.rid,
            cid=cid,
            jid=self.job_info.jid,
            my_status=self.my_status,
            resume_info=self.resume.dict(),
        )

    def gen_contact_job(self, job: Dict):
        return teacher.ContactJob(
            jid=self.job_info.jid,
            tid=self.resume.tid,
            rid=self.resume.rid,
            status=self.my_status,  # ContactJob.status is my_status
            job_info=job,
        )
        
    def fine_dict(self):
        dictionary = self.dict()
        dictionary["my_status"] = self.my_status.value
        return dictionary
