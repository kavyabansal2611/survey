from pydantic import BaseModel,EmailStr,Field
from typing import List,Literal
from sqlalchemy import Column,Integer,String,Text,ForeignKey
from database import Base
from pydantic import field_validator
class UserTable(Base):
    __tablename__="users"
    full_name=Column(String(100))
    email=Column(String(100),primary_key=True)
    gender=Column(String(10))
    age=Column(Integer)
class Submissions(Base):
    __tablename__="submissions"
    id=Column(Integer,primary_key=True,autoincrement=True)
    email=Column(String(100),ForeignKey("users.email"),nullable=False,unique=True)
    chosen_options=Column(Text)
class User(BaseModel):
    full_name:str=Field(min_length=1,max_length=100)
    age: int = Field(ge=16, le=30)
    gender:Literal["M","F"]
    email:EmailStr
class Quiz(BaseModel):
    id:int
    question:str
    options: List[str]

class Submit(BaseModel):
    email:EmailStr
    chosen_options:List[int]
    @field_validator("chosen_options")
    def must15(cls,v):
        if len(v)!=15:
            raise ValueError("Answer all 15 questions")
        return v



