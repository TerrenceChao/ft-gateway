from typing import Any, Dict, Union
from fastapi import status
from ...service_api import IServiceApi
from ....configs.exceptions import ServerException, ForbiddenException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class MediaService:
    def __init__(self, req: IServiceApi):
        self.req = req

    def get_upload_params(self, host: str, params: Dict):
        url = f"{host}/users/upload-params"
        result, err = self.req.simple_get(url=url, params=params)

        if err:
            log.error(f"MediaService.get_upload_params fail: [request get], host:%s, params:%s, result:%s, err:%s", host, params, result, err)
            raise ServerException(msg="get upload params error")

        return result

    def delete_file(self, host: str, params: Dict):
        url = f"{host}/users"
        result, msg, status_code, err = self.req.delete_with_statuscode(
            url=url, params=params)

        if err:
            log.error(f"MediaService.delete_file fail: [request delete], host:%s, params:%s, result:%s, msg:%s, status_code:%s, err:%s", host, params, result, msg, status_code, err)
            raise ServerException(msg="delete file error")

        if status_code == status.HTTP_403_FORBIDDEN:
            log.error(f"MediaService.delete_file fail: [request delete >> HTTP_403_FORBIDDEN], host:%s, params:%s, result:%s, msg:%s, status_code:%s, err:%s", host, params, result, msg, status_code, err)
            raise ForbiddenException(msg=msg)

        return result
