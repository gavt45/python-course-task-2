from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from todo_app.db import create_context_manager, crud

class TodoService:
    def __init__(self,
                 db_sess_maker: sessionmaker,
                 ) -> None:
        self._db = create_context_manager(db_sess_maker)
