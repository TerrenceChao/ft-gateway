from fastapi import APIRouter, \
    Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from ..req.authorization import AuthRoute, token_required
from ..res.response import res_success
from ...domains.cache import ICache
from ...domains.media.services.media_service import MediaService
from ...apps.resources.adapters import service_client, gw_cache
from ...configs.constants import PATHS
from ...configs.conf import REGION_HOST_MEDIA
from ...configs.exceptions import ClientException
from ...infra.utils.util import get_serial_num
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


router = APIRouter(
    prefix="/media",
    tags=["Media"],
    dependencies=[Depends(token_required)],
    route_class=AuthRoute,
    responses={404: {"description": "Not found"}},
)


async def get_media_host():
    return REGION_HOST_MEDIA


_media_service = MediaService(service_client)


@router.get("/{role}/{role_id}/upload-params")
async def upload_params(role: str,
                        role_id: str,
                        filename: str = Query(...),
                        # mime_type: str = Query(...),
                        media_host: str = Depends(get_media_host),
                        ):
    if not role in PATHS.keys():
        raise ClientException(
            msg="The 'role' should be 'teacher' or 'company'")

    serial_num = await get_serial_num(cache=gw_cache, role_id=role_id)
    result = await _media_service.get_upload_params(
        host=media_host,
        params={
            "serial_num": serial_num,
            "role": PATHS[role],
            "role_id": role_id,
            "filename": filename,
            # "mime_type": mime_type,
        })

    return res_success(data=result)


@router.get("/{role}/{role_id}/upload-params/icon")
async def icon_upload_params(role: str,
                             role_id: str,
                             filename: str = Query(...),
                             # mime_type: str = Query(...),
                             media_host: str = Depends(get_media_host),
                             ):
    if not role in PATHS.keys():
        raise ClientException(
            msg="The 'role' should be 'teacher' or 'company'")

    serial_num = await get_serial_num(cache=gw_cache, role_id=role_id)
    result = await _media_service.get_overwritable_upload_params(
        host=media_host,
        params={
            "serial_num": serial_num,
            "role": PATHS[role],
            "role_id": role_id,
            "filename": filename,
            # "mime_type": mime_type,
        }
    )

    return res_success(data=result)


@router.delete("/{role}/{role_id}")
async def remove(role: str,
                  role_id: str,
                  object_key: str = Query(...),
                  media_host: str = Depends(get_media_host),
                  ):
    if not role in PATHS.keys():
        raise ClientException(
            msg="The 'role' should be 'teacher' or 'company'")

    serial_num = await get_serial_num(cache=gw_cache, role_id=role_id)
    result = await _media_service.delete_file(
        host=media_host,
        params={
            "serial_num": serial_num,
            "object_key": object_key,
        })

    return res_success(data=result)


"""teacher's media schema

    data = {
        "section_id": "~~", TODO: main key
        "teacher_id": "~~", TODO: partition key
        "resume_id": "~~",
        "order": 3,
        "subject": "Educations",
        "context": {
            "1": {...},
            "2": {...},
            "3": {...},
        },
        TODO: type 1
        "media": {          TODO: "section_id/context"
            "1": {              TODO: "context.1"
                "1": {              TODO: "context.1.1"
                    "name": "xxx",
                    "hash": "md5(file)",  # partition key?
                    "size": "16M",
                    "total_chunks": 28,
                    "progress": 23,
                    "status": "uploading/break/done",
                    "chunks": [
                        "xxxx",
                        "xxxx",
                        "xxxx",
                        "xxxx",
                        ...
                    ]
                },
                "2": {...},         TODO: "context.1.2"
                "3": {...},         TODO: "context.1.3"
            },
            "2": {...},         TODO: "context.2"
            "3": {...},         TODO: "context.3"
        }
        
        TODO: type 2
        "media": {          TODO: "section_id/context"
            "1": [              TODO: "context.1"
                {                   TODO: "context.1.1"
                    "name": "xxx",
                    "hash": "md5(file)",  # partition key?
                    "size": "16M",
                    "total_chunks": 28,
                    "progress": 23,
                    "status": "uploading/break/done",
                    "chunks": [
                        "xxxx",
                        "xxxx",
                        "xxxx",
                        "xxxx",
                        ...
                    ]
                },
                {...},              TODO: "context.1.2"
                {...},              TODO: "context.1.3"
            ],
            "2": [...],         TODO: "context.2"
            "3": [...],         TODO: "context.3"
        }
    }

"""


"""company's media schema

    data = {
        "company_id": "~~", TODO: partition key/main key
        "name": "~~",
        "logo": "~~",
        "intro": "~~",
        "overview": {
            "title": "godaddy",
            "founded": "600,000,000 USD",
            "size": "600 people"
        },
        "sections": {
            "1": {
                "subject": "Who We Rre",
                "context": "We value ..."
            },
            "2": {...},
            "3": {...},
        },
        
        TODO: type 1
        "media": {          TODO: "company_id"
            "1": {          TODO: "company_id" (global)
                "name": "xxx",
                "hash": "md5(file)",  # partition key?
                "size": "16M",
                "total_chunks": 28,
                "progress": 23,
                "status": "uploading/break/done",
                "chunks": [
                    "xxxx",
                    "xxxx",
                    "xxxx",
                    "xxxx",
                    ...
                ]
            },
            "2": {...},     TODO: "company_id" (global)
            "3": {...},     TODO: "company_id" (global)
        }
        
        TODO: type 2
        "media": [          TODO: "company_id"
            {               TODO: "company_id" (global)
                "name": "xxx",
                "hash": "md5(file)",  # partition key?
                "size": "16M",
                "total_chunks": 28,
                "progress": 23,
                "status": "uploading/break/done",
                "chunks": [
                    "xxxx",
                    "xxxx",
                    "xxxx",
                    "xxxx",
                    ...
                ]
            },
            {...},          TODO: "company_id" (global)
            {...},          TODO: "company_id" (global)
        ]
    }
    
"""
