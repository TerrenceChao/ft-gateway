from typing import List, Optional
from pydantic import BaseModel
from ...domains.match.company.value_objects.c_value_objects import *
# from ...configs.conf import SEARCH_RESUME_URL_PATH
from .response import ResponseVO

'''[others]'''


class CompanyMatchDataResponseVO(ResponseVO):
    data: Optional[CompanyMatchDataVO] = None


class CompanyFollowAndContactResponseVO(ResponseVO):
    data: Optional[CompanyFollowAndContactVO] = None


'''[[base]]'''


class _BaseResumeData(BaseModel):
    url_path: Optional[str] = None


class _BaseResumeResponseVO(ResponseVO):
    pass


'''[contacted-resume]'''

# [[base-contacted-resume]]


class _BaseContactResumeData(ContactResumeVO, _BaseResumeData):
    pass


class ContactResumeResponseVO(_BaseResumeResponseVO):
    data: Optional[_BaseContactResumeData] = None


class _ContactResumeListData(BaseModel):
    list: List[_BaseContactResumeData] = []
    next_ts: Optional[int] = None


class ContactResumeListResponseVO(_BaseResumeResponseVO):
    data: _ContactResumeListData


'''[followed-resume]'''

# [[base-followed-resume]]


class _BaseFollowResumeData(FollowResumeVO, _BaseResumeData):
    pass


class FollowResumeResponseVO(_BaseResumeResponseVO):
    data: Optional[_BaseFollowResumeData] = None


class _FollowResumeListData(BaseModel):
    list: List[_BaseFollowResumeData] = []
    next_ts: Optional[int] = None


class FollowResumeListResponseVO(_BaseResumeResponseVO):
    data: _FollowResumeListData


'''[job]'''


class EnableJobResponseVO(ResponseVO):
    data: EnableJobVO


class JobResponseVO(ResponseVO):
    data: Optional[ReturnJobVO] = None


class _JobListData(BaseModel):
    list: List[ReturnJobVO] = []
    next_jid: Optional[int] = None


class JobListResponseVO(ResponseVO):
    data: _JobListData


'''[profile-job]'''


class _ProfileAndJobData(BaseModel):
    profile: ReturnCompanyProfileVO
    job: Optional[ReturnJobVO] = None


class CompanyProfileAndJobResponseVO(ResponseVO):
    data: Optional[_ProfileAndJobData] = None


'''[profile]'''


class CompanyProfileResponseVO(ResponseVO):
    data: Optional[ReturnCompanyProfileVO] = None
