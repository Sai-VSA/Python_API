from .. import schemas, util, database
from fastapi import FastAPI, Response, status, HTTPException, APIRouter
from typing import List

router = APIRouter(
    prefix = "/users",
    tags = ['Users'] #group name
)

cursor = database.cursor
conn = database.conn

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate):
    try:
        ##hash the password
        user.password = util.hashPassword(user.password)

        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s) RETURNING *;", (user.email, user.password))
        new_user = cursor.fetchone()
        conn.commit()
        return new_user
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= f"user with email {user.email} already exists.")

@router.get("/{id}", status_code = status.HTTP_200_OK, response_model=schemas.UserResponse)
async def get_user(id: int):
    cursor.execute("SELECT * FROM users WHERE id = %s LIMIT 1;", (id,))
    user = cursor.fetchone()
    if user:
        return user
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"user with id {id} does not exist.")