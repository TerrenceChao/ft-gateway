from typing import Any, Dict, Union
from ...services.service_requests import ServiceRequests
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class MediaService:
    def __init__(self, req: ServiceRequests):
        self.req = req


    def get_upload_params(self, host: str, params: Dict) -> (Union[None, Any], Union[None, str]):
        url=f"{host}/users/upload-params"
        return self.req.get(url=url, params=params) # result, err
    
    def delete_file(self, host: str, params: Dict) -> (Union[None, Any], Union[None, str], Union[None, str], Union[None, int]):
        url=f"{host}/users"
        return self.req.delete_with_statuscode(url=url, params=params) # result, msg, err, status_code

