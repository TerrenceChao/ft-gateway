from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from .....infra.db.nosql import match_teachers_schemas as teacher
from .....infra.db.nosql import match_companies_schemas as company
from ...public_value_objects import ResumeIndexVO, BaseJobVO
from .....configs.constants import Apply


class _BaseJobData(BaseModel):
    url_path: Optional[str] = None


class ContactJobVO(_BaseJobData):
    jid: int
    tid: int
    rid: int  # NOT ForeignKey
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    job_info: Optional[Dict] = None
    created_at: Optional[int] = None


class ContactJobListVO(BaseModel):
    list: List[ContactJobVO] = []
    next_ts: Optional[int] = None


class FollowJobVO(_BaseJobData):
    jid: int
    tid: int
    job_info: BaseJobVO
    created_at: Optional[int] = None


class FollowJobListVO(BaseModel):
    list: List[FollowJobVO] = []
    next_ts: Optional[int] = None


class ResumeSectionVO(BaseModel):
    sid: Optional[int] = None
    tid: int
    rid: int  # NOT ForeignKey
    order: int
    subject: str
    context: Dict


class ResumeVO(BaseModel):
    # rid: Optional[int] = None
    # tid: int
    intro: str
    sections: Optional[List[ResumeSectionVO]] = []
    tags: Optional[List[str]] = []
    enable: bool = True
    # it's optional in gateway
    published_in: str


class UpdateResumeVO(BaseModel):
    # rid: Optional[int] = None
    # tid: int
    intro: Optional[str] = None
    sections: Optional[List[ResumeSectionVO]] = []
    tags: Optional[List[str]] = []
    enable: Optional[bool] = True


class ReturnResumeVO(UpdateResumeVO):
    rid: Optional[int] = None
    tid: int
    # it's optional in gateway
    published_in: str


class ResumeListVO(BaseModel):
    list: List[ReturnResumeVO] = []
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
