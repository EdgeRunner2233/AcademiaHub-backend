# celery.py

from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings

# 设置默认 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AcademiaHub.settings')

# 创建 Celery 应用实例
app = Celery('AcademiaHub',
             broker='redis://:127.0.0.1:6379/4',
             backend='redis://:127.0.0.1:6379/5')

app.autodiscover_tasks(settings.INSTALLED_APPS)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.timezone = 'Asia/Shanghai'

app.autodiscover_tasks()




