from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from config import SQLALCHEMY_DATABASE_URL

IS_SQLITE = SQLALCHEMY_DATABASE_URL.startswith('sqlite')

if IS_SQLITE:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=30,
        pool_recycle=3600,
        pool_timeout=10
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_context_manager(sess_maker: sessionmaker):
    class ContextMan:  # Context Manager
        def __init__(self):
            self.db = sess_maker()

        def __enter__(self):
            return self.db

        def __exit__(self, exc_type, exc_value, traceback):
            if isinstance(exc_value, SQLAlchemyError):
                self.db.rollback()  # rollback on exception

            self.db.close()
    return ContextMan

GetDB = create_context_manager(SessionLocal)

from .models import *
from .crud import *