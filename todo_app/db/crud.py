from todo_app.db.models import *
from todo_app.models import User, Todo
from sqlalchemy.orm import Session, joinedload, noload, load_only, aliased, with_loader_criteria, Query
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func, funcfilter
from typing import List, Optional, Union, Tuple
import logging
from math import floor
from datetime import date
from traceback import format_exc

## Users things

def signup_user(db: Session, username: str, password: str) -> User:
    dbuser = DBUser(
        username=username,
        password=password,
    )

    db.add(dbuser)
    db.commit()
    db.refresh(dbuser)

    dbuser.password = None

    return User.from_orm(dbuser)

def get_user(db: Session, user_id: int = None, username: str = None) -> User:
    dbuser = None
    
    if username:
        dbuser = db.query(DBUser) \
                    .where(DBUser.username == username)
    elif user_id:
        dbuser = db.query(DBUser) \
                    .where(DBUser.id == user_id)
    
    dbuser = dbuser.first()
    
    if not dbuser:
        return None

    return User.from_orm(dbuser)

def delete_user_hard(db: Session, user_id: Optional[int] = None):
    q = db.query(DBUser)

    if user_id:
        q = q.filter_by(id=user_id)
    else:
        return
    
    dbuser: DBUser = q.first()

    if not dbuser:
        return None

    user = User.from_orm(dbuser)

    db.delete(dbuser)
    db.commit()

    return user

## Todos things

def get_todos(db: Session,
              user_id: Optional[int] = None,
              offset: Optional[int] = None,
              limit: Optional[int] = None,
              till: Optional[date] = None,
        ) -> List[Todo]:
    q = db.query(DBTodo)

    if till:
        q = q.filter(DBTodo.till <= till)

    if user_id:
        q = q.filter(DBTodo.user_id == user_id)
    
    if offset:
        q = q.offset(offset)
    
    if limit:
        q = q.limit(limit)
    
    # Disable default joined loading to filter explicitly
    q = q.options(noload(DBTodo.user))

    # if fetch_subscriptions:
    #     q = q.options(joinedload(DBUser.subscriptions))

    #     if not fetch_deleted_subs:
    #         q = q.options(with_loader_criteria(DBSubscription, DBSubscription.deleted_at == None))

    return [Todo.from_orm(u) for u in q.all()]

def create_todo(db: Session,
                user_id: int = None,
                till: date = None,
                description: str = "",
                ) -> Todo:
    
    dbtodo = DBTodo(
        user_id=user_id,
        description=description,
        till=till,
    )

    db.add(dbtodo)
    db.commit()
    db.refresh(dbtodo)

    dbtodo.user = None

    return Todo.from_orm(dbtodo)

def complete_todo(db: Session, user_id: int, todo_id: int) -> Todo:
    dbtodo: Query = db.query(DBTodo).filter(DBTodo.id == todo_id).filter(DBTodo.user_id == user_id)

    dbtodo = dbtodo.with_for_update()
    
    dbtodo: DBTodo = dbtodo.first()

    if not dbtodo:
        return None
    
    dbtodo.completed = True
    
    db.commit()
    db.refresh(dbtodo)

    dbtodo.user = None
    
    return Todo.from_orm(dbtodo)


def review_todos(db: Session, today: date):
    q: Query = db.query(DBTodo) \
                .filter(DBTodo.till < today) \
                .filter(DBTodo.completed == False)
    
    q.update({"till": today}, synchronize_session='evaluate')
    
    db.commit()