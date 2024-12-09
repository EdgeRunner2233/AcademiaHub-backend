# celery.py

from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

# 设置默认 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AcademiaHub.settings')

# 创建 Celery 应用实例
app = Celery('AcademiaHub')

# 使用 Django settings 文件配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的 Django app 中加载任务模块
app.autodiscover_tasks()


