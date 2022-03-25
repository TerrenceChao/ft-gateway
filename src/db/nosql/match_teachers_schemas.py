import json
from typing import Dict, List, Optional
from pydantic import BaseModel


class ContactJob(BaseModel):
    jid: int
    tid: int
    rid: int  # NOT ForeignKey
    enable: bool
    read: bool
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


class TeacherProfile(BaseModel):
    tid: int
    fullname: str
    email: str
    avator: Optional[str] = None
    brief_intro: Optional[str] = None
    is_verified: bool


class Teacher(TeacherProfile):
    resumes: Optional[List[Resume]] = None
    # TODO: deprecated >> resume_sections: Optional[List[ResumeSection]] = None
    follow_jobs: Optional[List[FollowJob]] = None
    contact_jobs: Optional[List[ContactJob]] = None
