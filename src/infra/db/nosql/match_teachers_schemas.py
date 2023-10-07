import json
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from .match_public_schemas import BaseEntity
from ....configs.constants import Apply


class ContactJob(BaseEntity):
    jid: int
    tid: int
    rid: int  # NOT ForeignKey
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    job_info: Optional[Dict] = None

    def fine_dict(self):
        dictionary = self.dict()
        dictionary["status"] = self.status.value
        dictionary["my_status"] = self.my_status.value
        return dictionary


class FollowJob(BaseEntity):
    jid: int
    tid: int
    job_info: Optional[Dict] = None


class ResumeSection(BaseEntity):
    sid: Optional[int] = None
    tid: int
    rid: int  # NOT ForeignKey
    order: int
    subject: str
    context: Dict


class Resume(BaseEntity):
    rid: Optional[int] = None
    tid: int
    intro: Optional[str] = None
    sections: Optional[List[ResumeSection]] = []
    tags: Optional[List[str]] = []
    enable: Optional[bool] = True
    # it's optional in gateway
    published_in: Optional[str] = None


class TeacherProfile(BaseEntity):
    tid: int
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    avator: Optional[str] = None
    brief_intro: Optional[str] = None
    is_verified: Optional[bool] = False


'''Teacher(TeacherProfile): Used for remote copies'''
class Teacher(TeacherProfile):
    resumes: Optional[List[Resume]] = []
    follow_jobs: Optional[List[FollowJob]] = []
    contact_jobs: Optional[List[ContactJob]] = []
