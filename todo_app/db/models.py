from __future__ import annotations

from sqlalchemy import (JSON, BigInteger, Boolean, Column, DateTime, Date, Enum,
                        Float, ForeignKey, Integer, String, Table,
                        UniqueConstraint)
from datetime import datetime, date
import uuid

from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql.expression import text

from todo_app.db import Base

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(length=32), nullable=True)
    password = Column(String(length=256), nullable=False)

    todos = relationship("DBTodo", back_populates="user", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, default=None)


class DBTodo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("DBUser", back_populates="todos")

    completed = Column(Boolean, default=False, nullable=False)

    description = Column(String(length=512), nullable=False)

    till = Column(Date, default=date.today)

    created_at = Column(DateTime, default=datetime.utcnow)
