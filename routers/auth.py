import sys
sys.path.append("..")
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from pydantic import BaseModel
from db import SessionLocal, engine
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt
from datetime import datetime,timedelta
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from models import *
from sqlalchemy import or_
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oath_bearer=OAuth2PasswordBearer(tokenUrl='/auth/token')
templates = Jinja2Templates(directory='templates')

SECRET_KEY = 'testjwt'
ALGORITHM='HS256'
router=APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={401:{"user":"Not Authorized"}}
)

class LoginForm:
    def __init__(self, request: Request):
        self.request=request
        self.username:Optional[str]=None
        self.password:Optional[str]=None
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username=form.get('email')
        self.password=form.get('password')

def get_db():
    db=SessionLocal()
    try: 
        return db
    finally:
        db.close()
db_dep=Annotated[Session, Depends(get_db)]

def authenticate_user(username,password,db):
    user = db.query(User).filter(User.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.password):
        return False
    return user

def create_token(username,userid,userrole,time_delta):
    encode={'username':username,'id':userid,'role':userrole,'exp':datetime.utcnow()+time_delta}
    encoded_jwt=jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(request:Request):
    try:
        token = request.cookies.get('access_token')
        if token is None:
            return None
        payload = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
        username=payload['username']
        userid=payload['id']
        userrole=payload['role']
        if username is not None and userid is not None:
            return {'username':username,'userid':userid,'userrole':userrole}
    except:
        raise HTTPException(detail='Invalid user',status_code=status.HTTP_404_NOT_FOUND)

@router.post('/token')
async def auth_token(response:Response,form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    print(form_data.username)
    user= authenticate_user(form_data.username,form_data.password,db)
    if user:
        token = create_token(user.username,user.id,user.role,timedelta(minutes=60))
        response.set_cookie(key="access_token",value=token,httponly=True)
        return True
    else:
        return False

@router.get('/login_page',response_class=HTMLResponse)
async def login_page(request:Request):
    context = {'request':request}
    return templates.TemplateResponse('login.html',context=context)

@router.post('/',response_class=HTMLResponse)
async def login_user(request:Request, db:Session=Depends(get_db)):
    form = LoginForm(request)
    await form.create_oauth_form()
    response = RedirectResponse('/todo',status_code=status.HTTP_302_FOUND)

    token = await auth_token(response=response,form_data=form,db=db)

    if token:
        return response

    return templates.TemplateResponse('login.html',context={'request':request,'messages':{'alert':'danger','msg':'Invalid user'}})

@router.get('/register_page',response_class=HTMLResponse)
async def register_page(request:Request):
    context = {'request':request}
    return templates.TemplateResponse('register.html',context=context)

@router.post('/register')
async def user_register(
    request:Request,db:Session=Depends(get_db),email:str=Form(),username:str=Form(),
    firstname:str=Form(),lastname:str=Form(),password:str=Form(),password2:str=Form(),
    ):
    user= db.query(User).filter(or_(User.username==username,User.email==email)).first()

    if user and password!=password2:
        return templates.TemplateResponse('register.html',{'request':request,'messages':{'alert':'danger','msg':'Invalid registration.'}})
    
    user = User(
        username=username,
        first_name=firstname,
        last_name=lastname,
        password=bcrypt_context.hash(password),
        email=email,
        is_active=True,
        role='user'
    )
    db.add(user)
    db.commit()
    return templates.TemplateResponse('login.html',{'request':request,'messages':{'alert':'success','msg':'User created successfully'}})

@router.get('/logout')
async def logout(request:Request):
    respone = templates.TemplateResponse('login.html',{'request':request,'messages':{'alert':'success','msg':'Logout Successful'}})
    respone.delete_cookie('access_token')
    return respone


















# async def get_user(token:Annotated[str, Depends(oath_bearer)]):
#     payload = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
#     username=payload['username']
#     userid=payload['id']
#     userrole=payload['role']
#     if username is not None and userid is not None:
#         return {'username':username,'userid':userid,'userrole':userrole}
#     else:
#         raise HTTPException(detail='Invalid user',status_code=status.HTTP_404_NOT_FOUND)



# @router.post('/token')
# async def auth_token(response:Response,form:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dep):
#     user= authenticate_user(form.username,form.password,db)
#     if user:
#         token = create_token(user.username,user.id,user.role,timedelta(minutes=60))
#         return {'access_token':token,'token_type':'bearer'}
#     else:
#         raise HTTPException(detail='Invalid user',status_code=status.HTTP_404_NOT_FOUND)

# class UserRequest(BaseModel):
#     username:str
#     email:str
#     first_name:str
#     last_name:str
#     password:str
#     role:str

# class Token(BaseModel):
#     token:str

# @router.get('/users')
# async def get_users(db:db_dep):
#     return db.query(User).all()

# @router.post('/create_user')
# async def create_user(db:db_dep,user_req:UserRequest):
#     user_dict=user_req.model_dump()
#     user=User(
#             username=user_req.username,
#             email=user_req.email,
#             first_name=user_req.first_name,
#             last_name=user_req.last_name,
#             password=bcrypt_context.hash(user_req.password),
#             role=user_req.role
#         )
#     db.add(user)
#     db.commit()

#     return db.query(User).all()

# @router.put('/updateuser/{id}')
# async def update_user(db:db_dep,user_req:UserRequest,id:int):
#     user=db.query(User).filter(User.id==id).first()
#     user.username=user_req.username
#     user.email=user_req.email
#     user.first_name=user_req.first_name
#     user.last_name=user_req.last_name
#     user.password=bcrypt_context.hash(user_req.password)
#     user.role=user_req.role

#     db.add(user)
#     db.commit()

#     return db.query(User).all()