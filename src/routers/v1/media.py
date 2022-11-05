import io
import os
import time
import json
from typing import List, Dict, Any
from fastapi import APIRouter, \
    Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from pydantic import EmailStr
from ..res.response import res_success, res_err
from ...common.service_requests import get_service_requests
import boto3
from boto3.s3.transfer import TransferConfig
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


FT_BUCKET = os.getenv("FT_BUCKET", "foreign-teacher")
MULTIPART_THRESHOLD = int(os.getenv("MULTIPART_THRESHOLD", 512))
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", 10))
MULTIPART_CHUNKSIZE = int(os.getenv("MULTIPART_CHUNKSIZE", 128))


mediaConfig = TransferConfig(multipart_threshold=MULTIPART_THRESHOLD,
                             max_concurrency=MAX_CONCURRENCY,
                             multipart_chunksize=MULTIPART_CHUNKSIZE,
                             use_threads=True)
session = boto3.Session(
    aws_access_key_id="AKIAX77V6Z26DYCBVFAH",
    aws_secret_access_key="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"
)
# s3 = session.resource("s3")
# log.info(s3)
s3client = session.client("s3")
log.info(s3client)


region_media_hosts = {
    # "default": os.getenv("REGION_HOST_MEDIA", "http://localhost:8083/media/api/v1"),
    "jp": os.getenv("JP_REGION_HOST_MEDIA", "http://localhost:8083/media/api/v1"),
    "ge": os.getenv("GE_REGION_HOST_MEDIA", "http://localhost:8083/media/api/v1"),
    "us": os.getenv("US_REGION_HOST_MEDIA", "http://localhost:8083/media/api/v1"),
}


router = APIRouter(
    prefix="/media",
    tags=["Media"],
    responses={404: {"description": "Not found"}},
)


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
