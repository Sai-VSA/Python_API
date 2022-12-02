from .. import schemas, util, database, oath2
from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import List


cursor = database.cursor
conn = database.conn

router = APIRouter(
    tags = ['Authentication']
)

@router.post('/login', response_model=schemas.tokenSchema)
# {
    # username: ///email
    # password: ///password
# }
async def userLogin(userCredentials: OAuth2PasswordRequestForm = Depends()):
    try:
        cursor.execute('SELECT * FROM users WHERE email = %s LIMIT 1', (userCredentials.username,))
        stored_user = cursor.fetchone()
        if util.verifyPassword(stored_user['password'], userCredentials.password):
            access_token = oath2.create_access_token(data = {"user_id": stored_user['id']})
            return {'access_token' : access_token, 'token_type' : 'bearer'}
        else:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Invalid credentials.")
    except Exception as error:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Invalid credentials.")



