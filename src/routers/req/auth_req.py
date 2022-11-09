from pydantic import BaseModel, EmailStr


class SignupVO(BaseModel):
    email: EmailStr
    meta: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "meta": "{\"region\":\"jp\",\"role\":\"teacher\",\"pass\":\"secret\"}",
            }
        }
        
class SignupConfirmVO(BaseModel):
    email: EmailStr
    confirm_code: str
    pubkey: str = None
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "confirm_code": "106E7B",
                "pubkey": "the-pubkey"
            }
        }
        
class LoginVO(BaseModel):
    client_region: str = None, # this.header, auth-service.body
    email: EmailStr
    meta: str
    prefetch: int = None
    pubkey: str = None
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "meta": "{\"region\":\"jp\",\"role\":\"teacher\",\"pass\":\"secret\"}",
                "prefetch": None,
                "pubkey": "the-pubkey"
            }
        }