from typing import List, Optional, Union
from pydantic import BaseModel
from ...domains.user.value_objects.auth_vo import AuthVO, PubkeyVO
from ...domains.match.company.value_objects.c_value_objects import CompanyMatchDataVO
from ...domains.match.teacher.value_objects.t_value_objects import TeacherMatchDataVO
from .response import ResponseVO


class WelcomeResponseVO(ResponseVO):
    data: PubkeyVO

class _SignupData(BaseModel):
    auth: AuthVO

class SignupResponseVO(ResponseVO):
    data: _SignupData
    
    
class _LoginData(_SignupData):
    match: Union[CompanyMatchDataVO, TeacherMatchDataVO]

class LoginResponseVO(ResponseVO):
    data: _LoginData