import json
from typing import Dict, List, Optional
from pydantic import BaseModel
from .match_public_schemas import BaseEntity
from ....configs.constants import Apply

class ContactResume(BaseEntity):
    rid: int
    cid: int
    jid: int  # NOT ForeignKey
    status: Optional[Apply] = Apply.PENDING
    my_status: Optional[Apply] = Apply.PENDING
    resume_info: Optional[Dict] = None

    def fine_dict(self):
        dictionary = self.dict()
        dictionary["status"] = self.status.value
        dictionary["my_status"] = self.my_status.value
        return dictionary


class FollowResume(BaseEntity):
    rid: int
    cid: int
    resume_info: Optional[Dict] = None


class Job(BaseEntity):
    jid: Optional[int] = None
    cid: int
    title: Optional[str] = None
    region: Optional[str] = None
    salary: Optional[str] = None
    job_desc: Optional[Dict] = None
    # extra data, photos
    others: Optional[Dict] = None
    tags: Optional[List[str]] = []
    enable: Optional[bool] = True
    # it's optional in gateway
    published_in: Optional[str] = None


class CompanyProfile(BaseEntity):
    cid: int
    name: Optional[str] = None
    intro: Optional[str] = None
    logo: Optional[str] = None
    # size, founded, revenue, ... etc (json)
    overview: Optional[Dict] = None
    # who, what, where, ... etc (json array)
    sections: Optional[List[Dict]] = []
    photos: Optional[List[Dict]] = []


'''Company(CompanyProfile): Used for remote copies'''
class Company(CompanyProfile):
    jobs: Optional[List[Job]] = []
    follow_resumes: Optional[List[FollowResume]] = []
    contact_resumes: Optional[List[ContactResume]] = []
