from typing import Any
from pydantic import create_model

# ref: https://github.com/tiangolo/fastapi/issues/3737

def response_vo(route: str, schema: Any):
    return create_model(route, code=(str, ...), msg=(str, ...), data=(schema, ...))
