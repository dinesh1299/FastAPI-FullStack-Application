from fastapi import APIRouter, Depends, HTTPException, status
from models import *
from db import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel
from .auth import get_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db=SessionLocal()
    try: 
        return db
    finally:
        db.close()
    

db_dep=Annotated[Session,Depends(get_db)]
user_dep=Annotated[dict, Depends(get_user)]


@router.get('/get_todos')
async def get_todos(user:user_dep,db:db_dep):
    if user['userrole']=='admin':
        return db.query(Todo).all()
    else:
        raise HTTPException(detail='You not allowed to view this page',status_code=status.HTTP_401_UNAUTHORIZED)