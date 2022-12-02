from jose import JWTError, jwt
from . import database, schemas
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer



oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'login') ## endpoint where token is generated

## Server Data KEY
## Algorithm HS256
## Token expiration time

SECRET_KEY = database.os.getenv('SECRET_KEY')
Algorithm = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

## takes a dict with userID and creates a JWT token with userID and expiration time as Payload
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = Algorithm)

    return encoded_jwt

## Decodes given JWT access token and validates stored data
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[Algorithm])

        id:str = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = schemas.tokenData(id = id)
    except JWTError:
        raise credentials_exception
    return token_data 

## helps add a dependency to other functions to ensure user is logged in
## gets called whenever a particular endpoint is reached
def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = f"Could not validate credentials."
        , headers={"WWW-Authenticate": "Bearer"})

    try: 
        token = verify_access_token(token, credentials_exception)
        database.cursor.execute("SELECT * FROM users WHERE id = %s LIMIT 1;", (token.id,))
        stored_user = database.cursor.fetchone()
        print(stored_user)
        return stored_user
    except JWTError:
        raise credentials_exception
