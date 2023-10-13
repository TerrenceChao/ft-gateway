from fastapi import Header, Body
from ...domains.user.value_objects.auth_vo import *


def signup_check_body(region: str = Header(...),
                      body: SignupVO = Body(...)
                      ) -> (SignupVO):
    body.region = region
    return body


def login_check_body(current_region: str = Header(...),
                     body: LoginVO = Body(...)
                     ) -> (LoginVO):
    body.current_region = current_region
    return body
