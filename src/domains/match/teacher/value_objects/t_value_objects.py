from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from .....infra.db.nosql import match_teachers_schemas as teacher
from .....infra.db.nosql import match_companies_schemas as company
from ...public_value_objects import ResumeIndexVO, BaseJobVO
from .....configs.constants import Apply
from .....configs.conf import SEARCH_JOB_URL_PATH


class _BaseJobData(BaseModel):
    url_path: Optional[str] = None
    
    def init(self):
        if self.job_info != None:
            job = self.job_info
            self.url_path = f'{SEARCH_JOB_URL_PATH}/{job.region}/{job.cid}/{job.jid}'
        return self


class ContactJobVO(_BaseJobData):
    jid: int
    tid: int
    rid: int  # NOT ForeignKey
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    job_info: Optional[BaseJobVO] = None
    created_at: Optional[int] = None


class ContactJobListVO(BaseModel):
    list: List[ContactJobVO] = []
    next_ts: Optional[int] = None
    
    def init(self):
        [item.init() for item in self.list]
        return self


class FollowJobVO(_BaseJobData):
    jid: int
    tid: int
    job_info: BaseJobVO
    created_at: Optional[int] = None


class FollowJobListVO(BaseModel):
    list: List[FollowJobVO] = []
    next_ts: Optional[int] = None
    
    def init(self):
        [item.init() for item in self.list]
        return self


class ResumeSectionVO(BaseModel):
    sid: Optional[int] = 0
    tid: Optional[int] = None # validation check
    rid: Optional[int] = None # validation check
    order: Optional[int] = None # validation check | display order
    category: Optional[str] = None # Education, Experience, Project, Certificate, Skill, Language
    logo: Optional[str] = None
    name: Optional[str] = None # School, Company, Certificate Name, Skill Name
    title: Optional[str] = None # Degree, Job Title
    location: Optional[str] = None # School Location, Company Location
    start_year: Optional[int] = None
    start_month: Optional[int] = None
    end_year: Optional[int] = None
    end_month: Optional[int] = None
    context: Optional[Dict] = None # Study Subject, Company Industry, Description, image/file urls, others
    updated_at: Optional[int] = None
    
    def upsert_msg(self):
        if self.sid == 0 or self.sid is None:
            return 'resume section is created'
        else:
            return 'resume section is udpated'
    

class ReturnResumeSectionVO(ResumeSectionVO):
    sid: int
    tid: int
    rid: int  # NOT ForeignKey
    order: int # display order
    category: str
    context: Dict


class ResumeVO(BaseModel):
    # rid: Optional[int] = None
    # tid: int
    intro: str
    # sections: Optional[List[ResumeSectionVO]] = []
    tags: Optional[List[str]] = []
    enable: bool = True
    # it's optional in gateway
    region: str


class UpdateResumeVO(BaseModel):
    # rid: Optional[int] = None
    # tid: int
    intro: Optional[str] = None
    # sections: Optional[List[ResumeSectionVO]] = []
    tags: Optional[List[str]] = []
    enable: Optional[bool] = True


class BriefResumeVO(UpdateResumeVO):
    rid: Optional[int] = None
    tid: int
    # it's optional in gateway
    region: str


class ReturnResumeVO(BriefResumeVO):
    sections: Optional[List[ResumeSectionVO]] = []


class ResumeListVO(BaseModel):
    list: List[BriefResumeVO] = []
    next_rid: Optional[int] = None


class EnableResumeVO(BaseModel):
    rid: int
    tid: int
    enable: bool


class TeacherProfileVO(BaseModel):
    # tid: int
    fullname: str
    email: EmailStr
    avator: Optional[str] = None
    brief_intro: Optional[str] = None
    is_verified: bool = False


class UpdateTeacherProfileVO(BaseModel):
    # tid: int
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    avator: Optional[str] = None
    brief_intro: Optional[str] = None
    is_verified: Optional[bool] = False


class ReturnTeacherProfileVO(UpdateTeacherProfileVO):
    tid: int


class TeacherVO(TeacherProfileVO):
    brief_resumes: Optional[List[ReturnResumeVO]] = []
    followed: Optional[List[FollowJobVO]] = []
    contact: Optional[List[ContactJobVO]] = []


class TeacherMatchDataVO(BaseModel):
    brief_resumes: Optional[List[ReturnResumeVO]] = []
    followed: Optional[List[FollowJobVO]] = []
    contact: Optional[List[ContactJobVO]] = []


class TeacherFollowAndContactVO(BaseModel):
    followed: Optional[List[FollowJobVO]] = []
    contact: Optional[List[ContactJobVO]] = []


class ApplyJobVO(BaseModel):
    # register_region: Optional[str] = None
    current_region: str
    my_status: Apply
    # status: Optional[Apply] = Apply.PENDING
    job: BaseJobVO
    resume_info: ResumeIndexVO

    def fine_dict(self):
        dictionary = self.dict()
        dictionary["my_status"] = self.my_status.value
        return dictionary


class TeacherProfileAndResumeVO(BaseModel):
    profile: ReturnTeacherProfileVO
    # for search API, need created/updated/last_updated time
    resume: Optional[teacher.Resume] = None
    
    '''
    hide sensitive data
    '''
    def public_info(self):
        self.profile.email = None
        self.profile.is_verified = None
        return self
