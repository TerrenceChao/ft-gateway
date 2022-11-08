import json
from typing import Dict, List, Optional
from pydantic import BaseModel


class ContactResume(BaseModel):
    rid: int
    cid: int
    jid: int  # NOT ForeignKey
    enable: bool
    read: bool
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


class CompanyProfile(BaseModel):
    cid: int
    name: str
    logo: Optional[str] = None
    intro: str
    overview: Dict  # size, founded, revenue, ... etc (json)
    sections: List[Dict]  # who, what, where, ... etc (json array)
    photos: Optional[Dict] = None

    def dynamo_serialize(self):
        return {
            "cid": {"N": str(self.cid)},
            "name": {"S": str(self.name)},
            "logo": {"S": str(self.logo)},
            "intro": {"S": str(self.intro)},
            "overview": {"S": json.dumps(self.overview)},
            "sections": {"S": json.dumps(self.sections)},
            "photos": {"S": json.dumps(self.photos)}
        }


# for response model
class UpsertCompanyProfileJob(BaseModel):
    profile: CompanyProfile = None
    resume: Job


class Company(CompanyProfile):
    jobs: Optional[List[Job]] = None
    follow_resumes: Optional[List[FollowResume]] = None
    contact_resumes: Optional[List[ContactResume]] = None
