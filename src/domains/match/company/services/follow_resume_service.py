from typing import Any, List, Dict
from ....service_api import IServiceApi
from .....domains.match.company.value_objects import c_value_objects as com_vo
from .....configs.exceptions import \
    ClientException, ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class FollowResumeService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def upsert_follow_resume(self, host: str, company_id: int, resume_id: int, resume_info: com_vo.BaseResumeVO):
        data, err = self.req.simple_put(
            url=f"{host}/companies/{company_id}/follow/resumes/{resume_id}",
            json=resume_info.dict()
        )
        if err:
            log.error(
                f"{self.__class__.__name__}.upsert_follow_resume fail: [request post],\
                    host:%s, company_id:%s, resume_id:%s, resume_info:%s, data:%s, err:%s",
                host, company_id, resume_id, resume_info, data, err)
            raise ServerException(msg=err)

        return data

    def get_followed_resume_list(self, host: str, company_id: int, size: int, next_ts: int = None):
        data, err = self.req.simple_get_list(
            url=f"{host}/companies/{company_id}/follow/resumes",
            params={
                "size": size,
                "next_ts": next_ts,
            })

        if err:
            log.error(f"{self.__class__.__name__}.get_followed_resume_list fail: [request get],\
                host:%s, company_id:%s, size:%s, next_ts:%s, data:%s, err:%s",
                      host, company_id, size, next_ts, data, err)
            raise ServerException(msg=err)

        return data

    def delete_followed_resume(self, host: str, company_id: int, resume_id: int):
        data, err = self.req.simple_delete(
            url=f"{host}/companies/{company_id}/follow/resumes/{resume_id}")
        if err:
            log.error(f"{self.__class__.__name__}.delete_followed_resume fail: [request post],\
                host:%s, company_id:%s, data:%s, err:%s",
                      host, company_id, data, err)
            raise ServerException(msg=err)

        return data
