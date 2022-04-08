import os
import time
import json
import requests
from typing import List, Dict, Any
from unicodedata import name
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from ..res.response import res_success, res_err
import logging as log


region_media_hosts = {
    # "default": os.getenv("REGION_HOST_MEDIA", "http://localhost:8083/media/api/v1"),
    "jp": os.getenv("JP_REGION_HOST_MEDIA", "http://localhost:8083/media/api/v1"),
    "ge": os.getenv("EU_REGION_HOST_MEDIA", "http://localhost:8083/media/api/v1"),
    "us": os.getenv("US_REGION_HOST_MEDIA", "http://localhost:8083/media/api/v1"),
}

log.basicConfig(level=log.INFO)


router = APIRouter(
    prefix="/media",
    tags=["Media"],
    responses={404: {"description": "Not found"}},
)


@router.post("/teachers/{teacher_id}/resumes/{resume_id}/sections/{section_id}/files")
async def upload_files_by_teacher(
    teacher_id: int,
    resume_id: int,
    section_id: int
):
    pass


@router.post("/companies/{company_id}/metadata")
async def create_metadata_by_company(company_id: int):
    pass


@router.post("/companies/{company_id}/files")
async def upload_media_files_by_company(company_id: int):
    pass


@router.put("/companies/{company_id}/echo")
async def echo_by_company(company_id: int):
    pass







"""teacher's media schema

  data = {
    "section_id": "~~",
    "teacher_id": "~~",
    "resume_id": "~~",
    "order": 3,
    "subject": "Educations",
    "context": {
      1: {...}, 
      2: {...}, 
      3: {...},
    },
    "media": {
      1: {
        "pic1(ordered)": {
          "name": "xxx",
          "hash": "md5(file)", # partition key?
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
        "pic2": {...},
        "pic3": {...},
      }, 
      2: {...}, 
      3: {...},
    }
  }
"""
@router.post("/media/teachers/{teacher_id}/uploading")
def upload_media_files_by_teacher():
    pass


@router.post("/media/companies/{company_id}/uploading")
def upload_media_files_by_company():
    data = {
        "company_id": "~~",
        "name": "~~",
        "logo": "~~",
        "intro": "~~",
        "overview": {
            "title": "godaddy",
            "founded": "600,000,000 USD",
            "size": "600 people"
        },
        "sections": {
            1: {
                "subject": "Who We Rre",
                "context": "We value ..."
            },
            2: {...},
            3: {...},
        },
        "media": {
            "pic1(ordered)": {
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
            "pic2": {...},
            "pic3": {...},
        }
    }
    pass

