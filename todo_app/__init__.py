from __future__ import absolute_import

from apscheduler.schedulers.background import BackgroundScheduler

from fastapi import FastAPI
import logging

from config import UVICORN_HOST, \
                    UVICORN_PORT, UVICORN_UDS, DEBUG

LOGGING_FORMAT = "%(asctime)s [%(threadName)-12.12s] [%(filename)s:%(lineno)s] [%(levelname)s] %(message)s"

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format=LOGGING_FORMAT,
    handlers=[
        logging.StreamHandler()
    ]
)

scheduler = BackgroundScheduler({'apscheduler.job_defaults.max_instances': 20}, timezone='UTC')
logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

app = FastAPI()

from todo_app.db import SessionLocal

# Initialize service itself
from todo_app.service import TodoService

service = TodoService(
    SessionLocal,
)

from todo_app.jobs import *

from todo_app import handlers # noqa

@app.on_event("startup")
def startup():
    scheduler.start()

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()