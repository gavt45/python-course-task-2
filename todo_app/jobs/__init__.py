
from todo_app import scheduler, service
from todo_app.db import GetDB, crud

import logging
from datetime import datetime, timedelta

# Super-dirty implementation of todo date move
def review_todos():
    now = datetime.now()

    logging.info("Reviewing todos")
    with GetDB() as db:
       crud.review_todos(db, today=now.date())

scheduler.add_job(review_todos, 'interval', minutes=10, coalesce=True, max_instances=1)