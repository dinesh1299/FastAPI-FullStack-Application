from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from models import *
from db import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel
from .auth import get_user
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(
    prefix='/todo',
    tags=['todo']
)

templates = Jinja2Templates(directory='templates')

def get_db():
    db=SessionLocal()
    try: 
        return db
    finally:
        db.close()
class TodoRequest(BaseModel):
    title:str
    description:str
    priority:int
    complete:bool  

db_dep:Session=Annotated[Session,Depends(get_db)]
user_dep=Annotated[dict, Depends(get_user)]

@router.get('/',response_class=HTMLResponse)
async def get_todos(request:Request,db:db_dep):
    token = await get_user(request=request)
    if token is None:
        return RedirectResponse(url='/auth/login_page',status_code=status.HTTP_302_FOUND)
    todos = db.query(Todo).filter(Todo.auth_user_id==token.get('userid')).all()

    return templates.TemplateResponse('home.html',{'request':request,'todos':todos,'user':True})

@router.get('/add_todo',response_class=HTMLResponse)
async def create_todo(request:Request):
    token = await get_user(request=request)
    if token is None:
        return RedirectResponse(url='/auth/login_page',status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse('add-todo.html',{'request':request,'user':True})

@router.post('/add_todo',response_class=RedirectResponse)
async def add_todo(request:Request,db:db_dep,title:str=Form(...),description:str=Form(...),
                   priority:int=Form(...)):
    token = await get_user(request=request)
    if token is None:
        return RedirectResponse(url='/auth/login_page',status_code=status.HTTP_302_FOUND)
    todo = Todo()
    todo.title=title
    todo.description=description
    todo.priority=priority
    todo.auth_user_id=token.get('userid')

    db.add(todo)
    db.commit()

    return RedirectResponse(url='/todo',status_code=status.HTTP_302_FOUND)

@router.get('/edit_todo/{id}',response_class=HTMLResponse)
async def edit_todo(request:Request,db:db_dep,id:int):
    token = await get_user(request=request)
    if token is None:
        return RedirectResponse(url='/auth/login_page',status_code=status.HTTP_302_FOUND)
    todo = db.query(Todo).filter(Todo.id==id).first()
    return templates.TemplateResponse('edit-todo.html',{'request':request,'todo':todo,'user':True})

@router.post('/edit_todo/{id}')
async def update_todo(request:Request,db:db_dep,id:int,title:str=Form(...),description:str=Form(...),
                   priority:int=Form(...)):
    token = await get_user(request=request)
    if token is None:
        return RedirectResponse(url='/auth/login_page',status_code=status.HTTP_302_FOUND)
    todo = db.query(Todo).filter(Todo.id==id).first()

    todo.title=title
    todo.description=description
    todo.priority=priority

    db.add(todo)
    db.commit()

    return RedirectResponse('/todo',status_code=status.HTTP_302_FOUND)

@router.get('/delete_todo/{id}')
async def delete_todo(id:int,request:Request,db:db_dep):
    token = await get_user(request=request)
    if token is None:
        return RedirectResponse(url='/auth/login_page',status_code=status.HTTP_302_FOUND)
    todo_item = db.query(Todo).filter(Todo.id==id).first()
    
    
    db.delete(todo_item)
    db.commit()

    return RedirectResponse('/todo',status_code=status.HTTP_302_FOUND)


@router.get('/todo_complete/{id}')
async def todo_complete(request:Request,id:int,db:db_dep):
    token = await get_user(request=request)
    if token is None:
        return RedirectResponse(url='/auth/login_page',status_code=status.HTTP_302_FOUND)
    todo=db.query(Todo).filter(Todo.auth_user_id==token.get('userid'),Todo.id==id).first()
   
    if todo and todo.complete:
        todo.complete = False
    elif todo and not todo.complete:
        todo.complete = True

    db.add(todo)
    db.commit()

    return RedirectResponse('/todo',status_code=status.HTTP_302_FOUND)















# @router.get('/get_todos')
# async def get_todos(db:db_dep):
#     return db.query(Todo).filter(Todo.auth_user_id==1).all()


# @router.get('/get_todo_by_id')
# async def get_todo(user:user_dep,db:db_dep,id:int):
#     todo=db.query(Todo).filter(Todo.id==id).filter(Todo.auth_user_id==user['userid']).first()
#     if todo:
#         return db.query(Todo).filter(Todo.id==id).filter(Todo.auth_user_id==user['userid']).all()
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Todo not found')


# @router.post('/create_todo')
# async def create_todo(user:user_dep,db:db_dep, todo_obj:TodoRequest):
#     todo_dict = todo_obj.model_dump()
    
#     todo_create=Todo(**todo_dict,auth_user_id=user['userid'])
#     db.add(todo_create)
#     db.commit()
    
#     return db.query(Todo).all()


# @router.put('/update_todo/{id}')
# async def update_todo(user:user_dep,db:db_dep,todo_obj:TodoRequest,id:int):
#     todo_item = db.query(Todo).filter(Todo.id==id).first()
#     todo_auth_id = todo_item.auth_user_id
#     if not todo_auth_id == user['userid']:
#         raise HTTPException(detail='You dont have permission to edit this',status_code=status.HTTP_403_FORBIDDEN)

#     if not todo_item:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="TOdo not found")

#     # for k,v in todo_obj.model_dump().items():
#     #     setattr(todo_item,k,v)

#     todo_item.title=todo_obj.title
#     todo_item.description=todo_obj.description
#     todo_item.complete=todo_obj.complete
#     todo_item.priority=todo_obj.priority

#     db.add(todo_item)
#     db.commit()
    
#     return db.query(Todo).all()


# @router.delete('/delete_todo')
# async def delete_todo(user:user_dep,db:db_dep,id:int):
#     todo_item = db.query(Todo).filter(Todo.id==id).filter(Todo.auth_user_id==user['userid']).first()

#     if not todo_item:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="TOdo not found")
    
#     db.delete(todo_item)
#     db.commit()

#     return db.query(Todo).all()


