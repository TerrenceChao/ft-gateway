from typing import Optional, Any
from pydantic import create_model, BaseModel

# ref: https://github.com/tiangolo/fastapi/issues/3737
def response_vo(route: str, schema: Any):
    return create_model(route, code=(str, ...), msg=(str, ...), data=(schema, ...))


def res_success(data=None, msg="ok", code="0"):
    return {
        "code": code,
        "msg": msg,
        "data": data,
    }


def res_err(data=None, msg="error", code="1"):
    return {
        "code": code,
        "msg": msg,
        "data": data,
    }

class ResponseVO(BaseModel):
    code: str = '0'
    msg: str = 'ok'
    data: Optional[Any] = None


'''[delete-Any]'''


class DeleteVO(ResponseVO):
    data: Optional[bool] = None
    