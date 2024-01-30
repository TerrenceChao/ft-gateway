from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class JobIndexVO(BaseModel):
    jid: int
    cid: int
    region: Optional[str] = None  # it's optional in gateway


class ResumeIndexVO(BaseModel):
    rid: int
    tid: int
    region: Optional[str] = None  # it's optional in gateway


class BaseJobVO(BaseModel):
    jid: int
    cid: int
    name: str  # company name
    logo: Optional[str] = None  # company logo
    title: str
    location: str
    salary: str
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    region: str


class BaseResumeVO(BaseModel):
    rid: int
    tid: int
    fullname: str  # teacher name
    avator: Optional[str] = None  # teacher avator
    intro: str
    region: str


class MarkVO(BaseModel):
    followed: Optional[bool]
    contacted: Optional[bool]
    
    def id(self) -> (int):
        pass
