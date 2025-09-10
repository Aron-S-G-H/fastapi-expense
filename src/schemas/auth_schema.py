from pydantic import BaseModel, field_validator, Field
from datetime import datetime
class AuthBaseSchema(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)

class LoginSchema(AuthBaseSchema):
    password: str = Field(..., max_length=255)
    
class RegisterSchema(AuthBaseSchema):
    password: str = Field(..., max_length=255)
    
class RegisterResponseSchema(AuthBaseSchema):
    id: int = Field(..., gt=0)
    created_at: datetime = Field(...)

class RefreshTokenSchema(BaseModel):
    refresh_token: str = Field(...)