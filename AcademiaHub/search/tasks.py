from AcademiaHub.celery import app
from search.models import *

import logging

logger = logging.getLogger('celeryFile')

@app.task
def add(x, y):
    return x + y


@app.task
def test():
    logger.info("successful !")

@app.task
def delete_search_weekly():
    SearchWork.objects.all().update(number=0)
    SearchWord.objects.all().update(number=0)