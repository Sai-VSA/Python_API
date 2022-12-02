from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True ##default to true if not provided

class PostCreate(PostBase):
    pass ##same as post base

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True

class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    poster: Optional[UserResponse]
    votes : int = 0
    class Config:
        orm_mode = True ##Pydantic expected a dict initially but this tells it to convert it anyway

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str

class tokenSchema(BaseModel):
    access_token: str
    token_type: str

class tokenData(BaseModel):
    id: Optional[str]

class vote(BaseModel):
    post_id: int
    user_id: int
    vote_status: int = Field(None, ge=-1, le=1)

    @validator('vote_status')
    def prevent_zero(cls, v):
        if v == 0:
            raise ValueError('0 is not a valid vote input')
        return v