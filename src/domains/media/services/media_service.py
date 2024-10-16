from typing import Any, Dict, Union
from fastapi import status
from ...service_api import IServiceApi
from ....configs.exceptions import ServerException, ForbiddenException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MediaService:
    def __init__(self, req: IServiceApi):
        self.req = req

    async def get_upload_params(self, host: str, params: Dict):
        url = f"{host}/users/upload-params"
        result = await self.req.simple_get(url=url, params=params)
        
        return result
    
    async def get_overwritable_upload_params(self, host: str, params: Dict):
        url = f"{host}/users/upload-params/overwritable"
        result = await self.req.simple_get(url=url, params=params)

        return result

    async def delete_file(self, host: str, params: Dict):
        url = f"{host}/users"
        result = await self.req.simple_delete(
            url=url, params=params)

        return result
