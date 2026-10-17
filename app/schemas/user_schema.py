from pydantic import BaseModel , ConfigDict , Field , EmailStr
from datetime import datetime
from typing import Annotated

class UserBase(BaseModel):
    name : Annotated[str ,Field(...,max_length=150 , title= "Name",description= "Name of User")]
    username : Annotated[str ,Field(...,max_length=150 , title= "Username",description= "Username for login")]
    email : Annotated[EmailStr , Field(...,max_length=150,title="Email" , description="Email of user")]


class UserCreate(UserBase):
    password : Annotated[str , Field(...,min_length=8 , max_length=16 , title="Password" , description="Password must be at least 8 characters long")]

class UserResponse(UserBase):
    user_id : int
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username : str
    password : str

class Token(BaseModel):
    access_token : str
    token_type : str
