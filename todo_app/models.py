from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, validator

class User(BaseModel):
    class Config:
        orm_mode = True
        from_attributes=True

    id: Optional[int]
    username: Optional[str]
    password: Optional[str]
    created_at: Optional[datetime]
    deleted_at: Optional[datetime]

class Todo(BaseModel):
    class Config:
        orm_mode = True
        from_attributes=True

    id: Optional[int]
    user_id: Optional[int]
    user: Optional[User]
    completed: Optional[bool]
    description: Optional[str]
    till: Optional[datetime]
    created_at: Optional[datetime]

# API models:

class TokenResponse(BaseModel):
    access_token: str

class SignupRequest(BaseModel):
    username: str
    password: str

class DirectLinkResponse(BaseModel):
    url: str

class TodoCreate(BaseModel):
    description: str
    till: Optional[str] = None
    
    @validator('till')
    def validate_date_format(cls, v):
        if v is not None:
            d = None

            try:
                d = datetime.strptime(v, "%d.%m.%Y").date()
            except ValueError:
                raise ValueError("Date must be in format DD.MM.YYYY")
            
            if d < date.today():
                raise ValueError("Date must be after or today")
            
            return d
        return v

