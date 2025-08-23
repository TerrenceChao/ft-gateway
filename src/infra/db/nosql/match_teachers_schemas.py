import json
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, EmailStr
from .base_schemas import BaseEntity
from ....configs.constants import Apply


class ContactJob(BaseEntity):
    jid: int
    tid: int
    rid: int  # NOT ForeignKey
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    job_info: Optional[Dict] = None

    def fine_dict(self):
        dictionary = self.model_dump()
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
    order: Optional[int] = None # display order
    category: Optional[str] = None # Education, Experience, Project, Certificate, Skill, Language
    logo: Optional[str] = None
    name: Optional[str] = None # School, Company, Certificate Name, Skill Name
    title: Optional[str] = None # Degree, Job Title
    location: Optional[str] = None # School Location, Company Location
    start_year: Optional[int] = None
    start_month: Optional[int] = None
    end_year: Optional[int] = None
    end_month: Optional[int] = None
    context: Dict # Study Subject, Company Industry, Description, image/file urls, others


class Resume(BaseEntity):
    rid: Optional[int] = None
    tid: int
    intro: Optional[str] = None
    sections: Optional[List[ResumeSection]] = []
    tags: Optional[List[str]] = []
    enable: Optional[bool] = True
    # it's optional in gateway
    region: Optional[str] = None


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
