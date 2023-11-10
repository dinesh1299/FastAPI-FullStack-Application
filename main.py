from fastapi import FastAPI
from models import *
from db import engine, Base
from routers import auth, todo,admin,users
from starlette.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

app.mount('/static',StaticFiles(directory='static'),name='static')

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(users.router)
Base.metadata.create_all(bind=engine)

if __name__=="__main__":
    uvicorn.run('main:app',host='127.0.0.1',port=4000,reload=True)

