import io
import os
import boto3
from boto3.s3.transfer import TransferConfig
from fastapi import APIRouter, \
    Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from pydantic import EmailStr
from ..req.authorization import AuthMatchRoute, token_required
from ..res.response import res_success
from ...configs.constants import SERIAL_KEY
from ...common.cache.cache import Cache
from ...common.cache.dynamodb_cache import get_cache
from ...services.service_requests import ServiceRequests
from ...configs.region_hosts import get_media_region_host
from ...services.media.media_service import MediaService
from ...exceptions.auth_except import ServerException, ClientException, ForbiddenException
from ...configs.conf import FT_BUCKET, MULTIPART_THRESHOLD, MAX_CONCURRENCY, MULTIPART_CHUNKSIZE, \
    AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


mediaConfig = TransferConfig(multipart_threshold=MULTIPART_THRESHOLD,
                             max_concurrency=MAX_CONCURRENCY,
                             multipart_chunksize=MULTIPART_CHUNKSIZE,
                             use_threads=True)
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3 = session.resource("s3")
log.info(s3)
s3client = session.client("s3")
log.info(s3client)


router = APIRouter(
    prefix="/media",
    tags=["Media"],
    dependencies=[Depends(token_required)],
    route_class=AuthMatchRoute,
    responses={404: {"description": "Not found"}},
)


def get_media_host(current_region: str = Header(...)):
    return get_media_region_host(region=current_region)


def get_serial_num(cache: Cache, role_id: str):
    user, cache_err = cache.get(role_id)
    if cache_err:
        raise ServerException(msg="unknown error")

    if not user or not SERIAL_KEY in user:
        raise ServerException(msg="user has no authrozanization")

    return user[SERIAL_KEY]


_media_service = MediaService(ServiceRequests())


@router.get("/{role}/{role_id}/upload-params")
def upload_params(role: str,
                  role_id: str,
                  filename: str = Query(...),
                  mime_type: str = Query(...),
                  media_host: str = Depends(get_media_host),
                  cache: Cache = Depends(get_cache),
                  ):
    if role != 'teachers' and role != 'companies':
        raise ClientException(msg="The 'role' should be 'teacher' or 'company'")

    serial_num = get_serial_num(cache=cache, role_id=role_id)
    result, err = _media_service.get_upload_params(
        host=media_host,
        params={
            "serial_num": serial_num,
            "role": role,
            "role_id": role_id,
            "filename": filename,
            "mime_type": mime_type,
        })
    if err:
        raise ServerException(msg="get upload params error")

    return res_success(data=result)


@router.delete("/{role}/{role_id}")
def remove(role: str,
           role_id: str,
           object_key: str = Query(...),
           media_host: str = Depends(get_media_host),
           cache: Cache = Depends(get_cache),
           ):
    if role != 'teachers' and role != 'companies':
        raise ClientException(msg="The 'role' should be 'teacher' or 'company'")

    serial_num = get_serial_num(cache=cache, role_id=role_id)
    result, msg, err, status_code = _media_service.delete_file(
        host=media_host,
        params={
            "serial_num": serial_num,
            "object_key": object_key,
        })

    if err:
        raise ServerException(msg="delete file error")

    if status_code == status.HTTP_403_FORBIDDEN:
        raise ForbiddenException(msg=msg)

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


@router.post("/teachers/{teacher_id}/resumes/{resume_id}/sections/{section_id}/files", status_code=201)
async def upload_files_by_teacher(
    teacher_id: int,
    resume_id: int,
    section_id: int,
    # files: List[UploadFile],
    file: UploadFile,
    email: EmailStr = Body(...),
):

    # TODO: call "match_service" first, check storage usage (storage space)

    # form = await request.form()
    # filename = form["file"].filename
    # contents = await form["file"].read()
    # log.info(contents)
    # s3client.upload_fileobj(io.BytesIO(b'abcdefg'), 'foreign-teacher', 'upload_files')
    # response = StreamingResponse(buff, media_type='text/plain')
    # log.info(type(request.stream()))
    log.info(email)

    buff = await file.read()
    s3client.upload_fileobj(
        Fileobj=io.BytesIO(buff),
        Bucket=FT_BUCKET,
        Key=f'{email}/{teacher_id}/{resume_id}/{section_id}/{file.filename}',
        Config=mediaConfig
    )

    log.info(len(buff))

    return {
        "name": file.filename,
        "content_type": file.content_type,
    }


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


@router.post("/companies/{company_id}/files", status_code=201)
async def upload_files_by_company(
    company_id: int,
    # files: List[UploadFile],
    file: UploadFile,
    email: EmailStr = Body(...),
):
    # TODO: call "match_service" first, check storage usage (storage space)

    log.info(email)

    buff = await file.read()
    s3client.upload_fileobj(
        Fileobj=io.BytesIO(buff),
        Bucket=FT_BUCKET,
        Key=f'{email}/{company_id}/{file.filename}',
        Config=mediaConfig
    )

    log.info(len(buff))

    return {
        "name": file.filename,
        "content_type": file.content_type,
    }
