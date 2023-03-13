import json
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from ...common.enums.apply import Apply


class ContactJob(BaseModel):
    jid: int
    tid: int
    rid: int  # NOT ForeignKey
    enable: bool
    read: bool
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    job_info: Dict


class FollowJob(BaseModel):
    jid: int
    tid: int
    follow: bool
    job_info: Dict


# class BaseSchema(BaseModel):
#   id: Optional[int] = None


class ResumeSection(BaseModel):
    sid: Optional[int] = None
    tid: int
    rid: int  # NOT ForeignKey
    order: int
    subject: str
    context: Dict


class Resume(BaseModel):
    rid: Optional[int] = None
    tid: int
    intro: Optional[str] = None
    enable: bool
    sections: Optional[List[ResumeSection]] = None


class SoftResume(BaseModel):
    rid: Optional[int] = None
    tid: int
    intro: Optional[str] = None
    enable: Optional[bool]
    sections: Optional[List[ResumeSection]] = None


class TeacherProfile(BaseModel):
    tid: int
    fullname: str
    email: EmailStr
    avator: Optional[str] = None
    brief_intro: Optional[str] = None
    is_verified: bool


class SoftTeacherProfile(BaseModel):
    tid: int
    fullname: Optional[str]
    email: Optional[EmailStr]
    avator: Optional[str] = None
    brief_intro: Optional[str] = None
    is_verified: Optional[bool]


# for response model
class UpsertTeacherProfileResume(BaseModel):
    profile: SoftTeacherProfile = None
    resume: SoftResume


class Teacher(TeacherProfile):
    resumes: Optional[List[Resume]] = None
    # TODO: deprecated >> resume_sections: Optional[List[ResumeSection]] = None
    follow_jobs: Optional[List[FollowJob]] = None
    contact_jobs: Optional[List[ContactJob]] = None
