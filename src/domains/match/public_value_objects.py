from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class JobIndexVO(BaseModel):
    jid: int
    cid: int
    published_in: Optional[str] = None  # it's optional in gateway


class ResumeIndexVO(BaseModel):
    rid: int
    tid: int
    published_in: Optional[str] = None  # it's optional in gateway
    
    
    
class BaseJobVO(BaseModel):
    jid: int
    cid: int
    name: str # company name
    logo: Optional[str] = None # company logo
    title: str
    region: str
    salary: str
    published_in: str


class BaseResumeVO(BaseModel):
    rid: int
    tid: int
    fullname: str # teacher name
    avator: Optional[str] = None # teacher avator
    intro: str
    published_in: str
