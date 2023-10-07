from typing import List, Optional, Any
from pydantic import BaseModel
from ...domains.match.teacher.value_objects.t_value_objects import *
# from ...configs.conf import SEARCH_JOB_URL_PATH
from .response import ResponseVO

'''[others]'''


class TeacherMatchDataResponseVO(ResponseVO):
    data: Optional[TeacherMatchDataVO] = None


class TeacherFollowAndContactResponseVO(ResponseVO):
    data: Optional[TeacherFollowAndContactVO] = None


'''[[base]]'''


class _BaseJobData(BaseModel):
    url_path: Optional[str] = None

    # def init(self):
    #     self.url_path = f'{SEARCH_JOB_URL_PATH}/{self.jid}'
    #     return self


class _BaseJobResponseVO(ResponseVO):
    pass
    # def init(self):
    #     if self.data is None:
    #         return None

    #     if isinstance(self.data, _BaseJobData):
    #         self.data = self.data.init()

    #     elif 'list' in self.data.__annotations__ and \
    #             isinstance(self.data.list, list):
    #         for item in self.data.list:
    #             if isinstance(item, _BaseJobData):
    #                 item = item.init()

    #     return self.data


'''[contacted-job]'''

# [[base-contacted-job]]


class _BaseContactJobData(ContactJobVO, _BaseJobData):
    pass


class ContactJobResponseVO(_BaseJobResponseVO):
    data: Optional[_BaseContactJobData] = None


class _ContactJobListData(BaseModel):
    list: List[_BaseContactJobData] = []
    next_ts: Optional[int] = None


class ContactJobListResponseVO(_BaseJobResponseVO):
    data: _ContactJobListData


'''[followed-job]'''

# [[base-followed-job]]


class _BaseFollowJobData(FollowJobVO, _BaseJobData):
    pass


class FollowJobResponseVO(_BaseJobResponseVO):
    data: Optional[_BaseFollowJobData] = None


class _FollowJobListData(BaseModel):
    list: List[_BaseFollowJobData] = []
    next_ts: Optional[int] = None


class FollowJobListResponseVO(_BaseJobResponseVO):
    data: _FollowJobListData


'''[resume]'''


class EnableResumeResponseVO(ResponseVO):
    data: EnableResumeVO


class ResumeResponseVO(ResponseVO):
    data: Optional[ReturnResumeVO] = None


class _ResumeListData(BaseModel):
    list: List[ReturnResumeVO] = []
    next_rid: Optional[int] = None


class ResumeListResponseVO(ResponseVO):
    data: _ResumeListData


'''[profile-resume]'''


class _ProfileAndResumeData(BaseModel):
    profile: ReturnTeacherProfileVO
    resume: Optional[ReturnResumeVO] = None


class TeacherProfileAndResumeResponseVO(ResponseVO):
    data: Optional[_ProfileAndResumeData] = None


'''[profile]'''


class TeacherProfileResponseVO(ResponseVO):
    data: Optional[ReturnTeacherProfileVO] = None
