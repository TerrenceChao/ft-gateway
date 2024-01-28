from typing import Tuple, Any, Set, List, Dict
from ..cache import ICache
from ..service_api import IServiceApi
from .public_value_objects import MarkVO
from ...configs.constants import COM, TEACH
from ...configs.exceptions import *
from ..user.value_objects.auth_vo import BaseAuthDTO
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class StarTrackerService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.req = req
        self.cache = cache

    def __role_target_ids(self, role: str) -> (Tuple[str, str]):
        if role in COM:
            return ('companies', 'resume_ids')
        elif role in TEACH:
            return ('teachers', 'job_ids')
        else:
            raise ClientException(msg='role is not correct')

    '''follow'''

    def __follow_key(self, role: str, role_id: int, target_ids: str) -> (str):
        role, target_ids = self.__role_target_ids(role)
        return f'{role}:{role_id}:follow:{target_ids}'

    def add_followed_star(self, role: str, role_id: int, target_id: int) -> (bool):
        role, target_ids = self.__role_target_ids(role)
        follow_set_key = self.__follow_key(role, role_id, target_ids)
        result = self.cache.sadd(follow_set_key, [target_id])
        return result > 0

    def remove_followed_star(self, role: str, role_id: int, target_id: int) -> (bool):
        role, target_ids = self.__role_target_ids(role)
        follow_set_key = self.__follow_key(role, role_id, target_ids)
        result = self.cache.srem(follow_set_key, target_id)
        return result > 0

    def followed_id_set(self, match_host: str, role: str, role_id: int) -> (Set[int]):
        role, target_ids = self.__role_target_ids(role)

        follow_set_key = self.__follow_key(role, role_id, target_ids)
        followed_set = self.cache.smembers(follow_set_key)
        if len(followed_set) > 0:
            return followed_set

        data = self.req.simple_get(
            url=f'{match_host}/{role}/{role_id}/follow/{target_ids}',
        )

        # TODO: confirm data is a list
        self.cache.sadd(follow_set_key, data)

        return data

    def followed_marks(self, match_host: str, role: str, role_id: int, target_list: List[MarkVO]):
        followed_id_set = self.followed_id_set(match_host, role, role_id)
        for target in target_list:
            target.followed = target.id() in followed_id_set

        return target_list

    '''contact'''

    def __contact_key(self, role: str, role_id: int, target_ids: str) -> (str):
        role, target_ids = self.__role_target_ids(role)
        return f'{role}:{role_id}:contact:{target_ids}'

    def add_contact_star(self, role: str, role_id: int, target_id: int) -> (bool):
        role, target_ids = self.__role_target_ids(role)
        contact_set_key = self.__contact_key(role, role_id, target_ids)
        result = self.cache.sadd(contact_set_key, [target_id])
        return result > 0

    def remove_contact_star(self, role: str, role_id: int, target_id: int) -> (bool):
        role, target_ids = self.__role_target_ids(role)
        contact_set_key = self.__contact_key(role, role_id, target_ids)
        result = self.cache.srem(contact_set_key, target_id)
        return result > 0

    def contact_id_set(self, match_host: str, role: str, role_id: int) -> (Set[int]):
        role, target_ids = self.__role_target_ids(role)

        contact_set_key = self.__contact_key(role, role_id, target_ids)
        contact_set = self.cache.smembers(contact_set_key)
        if len(contact_set) > 0:
            return contact_set

        data = self.req.simple_get(
            url=f'{match_host}/{role}/{role_id}/contact/{target_ids}',
        )

        # TODO: confirm data is a list
        self.cache.sadd(contact_set_key, data)

        return data

    def contact_marks(self, match_host: str, role: str, role_id: int, target_list: List[MarkVO]):
        contact_id_set = self.contact_id_set(match_host, role, role_id)
        for target in target_list:
            target.contacted = target.id() in contact_id_set

        return target_list

    def all_marks(self, match_host: str, visitor: BaseAuthDTO, target_list: List[MarkVO]):
        role = visitor.role
        role_id = visitor.role_id
        followed_id_set = self.followed_id_set(match_host, role, role_id)
        contact_id_set = self.contact_id_set(match_host, role, role_id)
        # 如果能看到 followed, contact 的星號，但自己沒有 follow, contact 的話，
        # 就表示有些 job, resume 的 id 是一樣的
        if len(followed_id_set) > 0 or len(contact_id_set) > 0:
            for target in target_list:
                target.followed = target.id() in followed_id_set
                target.contacted = target.id() in contact_id_set

        return target_list

