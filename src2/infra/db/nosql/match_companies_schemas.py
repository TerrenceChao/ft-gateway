import json
from typing import Dict, List, Optional
from pydantic import BaseModel
from ....configs.constants import Apply


class ContactResume(BaseModel):
    rid: int
    cid: int
    jid: int  # NOT ForeignKey
    enable: bool
    read: bool
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    resume_info: Dict


class FollowResume(BaseModel):
    rid: int
    cid: int
    follow: bool = True
    resume_info: Dict


# class BaseSchema(BaseModel):
#   id: Optional[int] = None


class Job(BaseModel):
    jid: Optional[int] = None
    cid: int
    title: str
    region: str
    salary: str
    job_desc: Dict
    others: Optional[Dict] = None  # extra data, photos
    enable: bool = True


class SoftJob(BaseModel):
    jid: Optional[int] = None
    cid: int
    title: Optional[str]
    region: Optional[str]
    salary: Optional[str]
    job_desc: Optional[Dict]
    others: Optional[Dict] = None  # extra data, photos
    enable: Optional[bool] = True


class CompanyProfile(BaseModel):
    cid: int
    name: str
    logo: Optional[str] = None
    intro: str
    overview: Dict  # size, founded, revenue, ... etc (json)
    sections: List[Dict]  # who, what, where, ... etc (json array)
    photos: Optional[List[Dict]] = None


class SoftCompanyProfile(BaseModel):
    cid: int
    name: Optional[str]
    logo: Optional[str] = None
    intro: Optional[str]
    overview: Optional[Dict]  # size, founded, revenue, ... etc (json)
    sections: Optional[List[Dict]]  # who, what, where, ... etc (json array)
    photos: Optional[List[Dict]] = None


# for response model
class UpsertCompanyProfileJob(BaseModel):
    profile: SoftCompanyProfile = None
    job: SoftJob


class Company(CompanyProfile):
    jobs: Optional[List[Job]] = None
    follow_resumes: Optional[List[FollowResume]] = None
    contact_resumes: Optional[List[ContactResume]] = None
