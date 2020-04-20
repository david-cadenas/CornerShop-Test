import os
from celery import Celery

app = Celery(
 broker=os.environ['CELERY_BROKER_URL'],
 include=('tasks')
)
