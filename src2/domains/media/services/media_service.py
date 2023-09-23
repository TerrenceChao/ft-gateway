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
        result, err = self.req.get(url=url, params=params)

        if err:
            raise ServerException(msg="get upload params error")

        return result

    def delete_file(self, host: str, params: Dict):
        url = f"{host}/users"
        result, msg, err, status_code = self.req.delete_with_statuscode(
            url=url, params=params)

        if err:
            raise ServerException(msg="delete file error")

        if status_code == status.HTTP_403_FORBIDDEN:
            raise ForbiddenException(msg=msg)

        return result
