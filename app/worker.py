from celery import Celery
import os


app = Celery(
 broker=os.environ['CELERY_BROKER_URL'],
 include=('tasks')
)
