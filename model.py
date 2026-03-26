from pydantic import BaseModel
from typing import List,Literal
from sqlalchemy import Column,Integer,String,Text
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
    id=Column(Integer,autoincrement=True)
    email=Column(String(100),primary_key=True)
    chosen_options=Column(Text)
class User(BaseModel):
    full_name:str
    age:int
    gender:Literal["M","F","O"]
    email:str
class Quiz(BaseModel):
    id:int
    question:str
    options: List[str]

class Submit(BaseModel):
    email:str
    chosen_options:List[int]
    @field_validator("chosen_options")
    def must15(cls,v):
        if len(v)!=15:
            raise ValueError("Answer all 15 questions")
        return v



