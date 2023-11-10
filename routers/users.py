from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from models import *
from db import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel
from .auth import get_user
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates 

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db=SessionLocal()
    try: 
        return db
    finally:
        db.close()

class ChangePassword(BaseModel):
    password:str   

db_dep=Annotated[Session,Depends(get_db)]
user_dep=Annotated[dict, Depends(get_user)]

@router.get('/get_users')
async def get_users(user:user_dep,db:db_dep):
    return db.query(User).filter(User.id==user['userid']).all()

@router.get('/change_password_page')
async def change_password_page(request:Request):
    return templates.TemplateResponse('reset_password.html',{'request':request})

@router.post('/change_password')
async def change_password(request:Request,db:db_dep,username:str=Form(),password:str=Form(),password2:str=Form()):
    print(username,password,password2)
    user_query=db.query(User).filter(User.username==username).first()
    print(user_query)
    if user_query and password==password2:
        user_query.password=bcrypt_context.hash(password)
        db.add(user_query)
        db.commit()
        msg = 'Password changed successfully'
        alert = 'success'
    else:
        msg = 'Invalid user'
        alert = 'danger'
    return templates.TemplateResponse('login.html',{'request':request,'messages':{'alert':alert,'msg':msg}})



# @router.post('/change_password')
# async def change_password(user:user_dep,db:db_dep,password_form:ChangePassword):
#     user_query=db.query(User).filter(User.id==user['userid']).first()
#     if user_query:
#         user_query.password=bcrypt_context.hash(password_form.password)
#         db.add(user_query)
#         db.commit()

#         return db.query(User).all()
#     else:
#         return 'Unauthorized access'