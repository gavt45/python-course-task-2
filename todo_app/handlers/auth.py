from todo_app import app
from todo_app.db import GetDB, crud
from todo_app.models import User, TokenResponse, SignupRequest

from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime, timezone
from typing import List, Annotated, Union

import jwt
from jwt.exceptions import InvalidTokenError
from config import JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
import logging

import traceback

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="./api/v1/login")

def get_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id: int = 0
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        user_id: int = int(payload.get("sub", -1))

        if user_id == -1:
            raise credentials_exception
    except InvalidTokenError:
        logging.warning(traceback.format_exc())
        raise credentials_exception

    with GetDB() as db:
        client = crud.get_user(db, user_id)
    
    if client is None:
        raise credentials_exception
    
    return client

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt

@app.post("/api/v1/login", response_model=TokenResponse)
def login(username: str = Form(), password: str = Form()) -> TokenResponse:
    client: User = None

    with GetDB() as db:
        client = crud.get_user(db, username=username)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client with such ID is not found",
        )

    if not pwd_context.verify(password, client.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong credentials",
        )
    
    access_token = create_access_token({"sub": str(client.id)}, expires_delta=timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES))

    return TokenResponse(access_token=access_token)

@app.post("/api/v1/signup", response_model=User)
def signup(req: SignupRequest = Form()) -> User:
    with GetDB() as db:
        client = crud.get_user(db, username=req.username)
    
    if client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username exists",
        )

    with GetDB() as db:
        client = crud.signup_user(db, 
                username=req.username,
                password=pwd_context.hash(req.password))

    return client