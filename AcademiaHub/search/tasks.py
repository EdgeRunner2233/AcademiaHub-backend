from AcademiaHub.celery import app
from search.models import *
from utils.search_utils import *

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

@app.task
def update_new_works():
    value = get_new150_works()
    works = value[0].get('results', [])
    unique_works = {work['id']: work for work in works}
    works = list(unique_works.values())
    cache.set('new_works', works, timeout=3700)
    NewWorks.objects.all().delete()
    # 存储数据到数据库
    for work in works:
        work_id = work['id']
        work_title = work['title']
        publication_date = work['publication_date']

        new_work, created = NewWorks.objects.get_or_create(
            work_id=work_id,
            defaults={
                'work_title': work_title,
                'publication_date': publication_date
            }
        )

        if not created:

            new_work.work_title = work_title
            new_work.publication_date = publication_date
            new_work.save()
