from db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class User(Base):
    __tablename__="user"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String,unique=True)
    email=Column(String,unique=True)
    first_name=Column(String)
    last_name=Column(String)
    password=Column(String)
    is_active=Column(Boolean,default=True)
    role=Column(String)
    phone=Column(String)

class Todo(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    auth_user_id=Column(Integer,ForeignKey('user.id'))
    