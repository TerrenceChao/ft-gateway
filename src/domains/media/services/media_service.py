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
        result = self.req.simple_get(url=url, params=params)
        
        return result
    
    def get_overwritable_upload_params(self, host: str, params: Dict):
        url = f"{host}/users/upload-params/overwritable"
        result = self.req.simple_get(url=url, params=params)

        return result

    def delete_file(self, host: str, params: Dict):
        url = f"{host}/users"
        result = self.req.simple_delete(
            url=url, params=params)

        return result
