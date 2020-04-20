import os

from billiard import Process
from celery.schedules import crontab
from worker import app

from CornerShopRichard.richardScraper import RichardScraper



@app.task(bind=True)
def richard(self):
    richard = RichardScraper()
    richard.load().clean().save()

app.conf.beat_schedule = {
    'wallmart-scrapper': {
        'task': 'tasks.richard',
        'schedule': crontab(hour='*/1'),
    },
}
