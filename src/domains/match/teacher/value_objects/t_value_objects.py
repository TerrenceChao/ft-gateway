from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from .....infra.db.nosql import match_teachers_schemas as teacher
from .....infra.db.nosql import match_companies_schemas as company
from ...public_value_objects import ResumeIndexVO, BaseJobVO
from .....configs.constants import Apply


class ContactJobVO(BaseModel):
    jid: int
    tid: int
    rid: int  # NOT ForeignKey
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    job_info: Optional[Dict] = None
    created_at: Optional[int] = None


class FollowJobVO(BaseModel):
    jid: int
    tid: int
    job_info: BaseJobVO
    created_at: Optional[int] = None


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
    published_in: Optional[str] = None

    def model(self, teacher_id: int):
        return teacher.Resume(
            tid=teacher_id,
            intro=self.intro,
            sections=self.sections,
            tags=self.tags,
            enable=self.enable,
            published_in=self.published_in
        )


class UpdateResumeVO(BaseModel):
    # rid: Optional[int] = None
    # tid: int
    intro: Optional[str] = None
    sections: Optional[List[ResumeSectionVO]] = []
    tags: Optional[List[str]] = []
    enable: Optional[bool] = True

    def model(self, teacher_id: int, resume_id: int):
        return teacher.Resume(
            rid=resume_id,
            tid=teacher_id,
            intro=self.intro,
            sections=self.sections,
            tags=self.tags,
            enable=self.enable,
        )


class ReturnResumeVO(UpdateResumeVO):
    rid: Optional[int] = None
    tid: int


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

    def model(self, teacher_id: int):
        return teacher.TeacherProfile(
            tid=teacher_id,
            fullname=self.fullname,
            email=self.email,
            avator=self.avator,
            brief_intro=self.brief_intro,
            is_verified=self.is_verified,
        )


class UpdateTeacherProfileVO(BaseModel):
    # tid: int
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    avator: Optional[str] = None
    brief_intro: Optional[str] = None
    is_verified: Optional[bool] = False

    def model(self, teacher_id: int):
        return teacher.TeacherProfile(
            tid=teacher_id,
            fullname=self.fullname,
            email=self.email,
            avator=self.avator,
            brief_intro=self.brief_intro,
            is_verified=self.is_verified,
        )


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
    current_region: Optional[str] = None
    my_status: Apply
    # status: Optional[Apply] = Apply.PENDING
    job: BaseJobVO
    resume_info: ResumeIndexVO

    # TODO: job 需要 hash code + 驗證，防竄改
    # job 是從外部傳入，不須在內部查找 DB
    def gen_contact_job(self, tid: int):
        return teacher.ContactJob(
            jid=self.job.jid,
            tid=tid,
            rid=self.resume_info.rid,
            my_status=self.my_status,
            job_info=self.job.dict(),
        )

    def gen_contact_resume(self, resume: Dict):
        return company.ContactResume(
            rid=self.resume_info.rid,
            cid=self.job.cid,
            jid=self.job.jid,
            status=self.my_status,  # ContactResume.status is my_status
            resume_info=resume,
        )
        
    def fine_dict(self):
        dictionary = self.dict()
        dictionary["my_status"] = self.my_status.value
        return dictionary
