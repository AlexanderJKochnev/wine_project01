# app/main.py
from fastapi import FastAPI
from app.support.users.router import router as user_router

# from app.support.major.router import router as major_router
# from app.support.student.router import router as student_router
# from app.support.users.router import router as user_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(user_router)
