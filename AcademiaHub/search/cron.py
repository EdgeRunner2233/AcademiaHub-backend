# from django_crontab import CronJobBase, Schedule
from django.utils.timezone import now
import logging
import os

from search.models import *

logger = logging.getLogger('mylogger')

print(f"环境变量 DJANGO_SETTINGS_MODULE：{os.environ.get('DJANGO_SETTINGS_MODULE')}")
def my_cron_job():
    logger.info(f"本地定时任务执行时间2：{now()}")
    print(f"本地定时任务执行时间111111111：{now()}")

def delete_search_work_models():
    SearchWork.objects.all().update(number=0)