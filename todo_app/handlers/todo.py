from todo_app import app
from todo_app.db import GetDB, crud
from todo_app.models import Todo, User, TodoCreate, DirectLinkResponse

from .auth import get_user

from datetime import date, datetime

from random import randbytes
from hashlib import sha256

from fastapi import Depends, Form, HTTPException, status, Query
from typing import List, Annotated, Union, Optional

def get_date_param(
    till: Optional[str] = Query(
        None,
        description="Date in DD.MM.YYYY format",
        example="30.12.2025"
    )
) -> Optional[date]:
    """Dependency that parses and validates DD.MM.YYYY date parameter"""
    if till is None:
        return None
    
    try:
        return datetime.strptime(till, "%d.%m.%Y").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Please use DD.MM.YYYY (e.g. 30.12.2025)"
        )

def get_mac(user_id: int, nonce: str):
    return sha256(f"{user_id}{nonce}".encode("ascii")).hexdigest()

@app.post("/api/v1/todo:create", response_model=Todo)
def create_todo(req: TodoCreate, client: User = Depends(get_user)):
    todo: Todo = None
    
    with GetDB() as db:
        todo = crud.create_todo(db, 
                                  client.id,
                                  till=req.till,
                                  description=req.description)
    
    return todo

@app.post("/api/v1/todo:complete", response_model=Todo)
def complete_todo(id: int, client: User = Depends(get_user)):
    todo: Todo = None
    
    with GetDB() as db:
        todo = crud.complete_todo(db, 
                                  user_id=client.id,
                                  todo_id=id)
    
    return todo

@app.get("/api/v1/todo", response_model=List[Todo])
def get_todos(till: Optional[date] = Depends(get_date_param), limit: Optional[int] = 100, offset: Optional[int] = 0, client: User = Depends(get_user)):
    with GetDB() as db:
        todos = crud.get_todos(db, limit=limit, offset=offset, till=till, user_id=client.id)
    
    return todos

@app.get("/api/v1/todo/share/{user_id}", response_model=List[Todo])
def get_todos(user_id: int, nonce: str, mac: str, till: Optional[date] = Depends(get_date_param), limit: Optional[int] = 100, offset: Optional[int] = 0):
    mac_true = get_mac(user_id, nonce)
    
    if mac != mac_true:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong url",
        )

    with GetDB() as db:
        todos = crud.get_todos(db, limit=limit, offset=offset, till=till, user_id=user_id)
    
    return todos

@app.post("/api/v1/todo:getDirectLink", response_model=DirectLinkResponse)
def get_direct_link(client: User = Depends(get_user)):
    nonce = randbytes(8)    
    
    return DirectLinkResponse(
        url=f"/api/v1/todo/share/{client.id}?nonce={nonce.hex()}&mac={get_mac(client.id, nonce.hex())}"
    )