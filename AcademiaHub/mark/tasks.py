from AcademiaHub.celery import app
from .models import *
from utils.search_utils import *

@app.task
def add_work_celery(work_id):
    work = get_single_work(work_id)
    if work:
        work['']


