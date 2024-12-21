"""
Django settings for AcademiaHub project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
import environ
from datetime import timedelta
from celery.schedules import crontab

env = environ.Env()
environ.Env.read_env(env_file='/Users/jsd/Desktop/AcademiaHub-backend/AcademiaHub/.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'history',
    'mark',
    'search',
    'work',
    'utils',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AcademiaHub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AcademiaHub.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'AcademiaHub',
        'USER':'root',
        'PASSWORD':env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT':'29086',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',  # 指定 Redis 作为缓存后端
        'LOCATION': 'redis://' + env('REDIS_HOST') + ':' + env('REDIS_PORT') + '/1',  # Redis 服务器的地址，127.0.0.1 是本地地址，6379 是 Redis 默认端口，/1 是数据库索引
        'OPTIONS': {
            'MAX_ENTRIES': env('REDIS_MAX_ENTRIES'),
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',  # 默认客户端配置
            # 'PASSWORD': '123456',
        },
        'TIMEOUT': 300,  # 设置缓存超时时间，单位为秒
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',  # 文件保存在当前目录
        },
        'celeryFile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'celery.log',  # 文件保存在当前目录
        },
    },
    'loggers': {
        'django': {
            'handlers': [],  # 不记录到文件
            'level': 'DEBUG',  # 只记录 WARNING 级别以上的日志
            'propagate': False,  # 防止 Django 默认的日志进入你设置的文件
        },
        'mylogger': {
            'handlers': ['file'],  # 记录到文件
            'level': 'DEBUG',  # 记录 DEBUG 级别及以上的日志
            'propagate': False,  # 防止传播到父级日志
        },
        'celery': {
            'handlers': ['celeryFile'],  # 记录到文件
            'level': 'DEBUG',  # 记录 DEBUG 级别及以上的日志
            'propagate': False,  # 防止传播到父级日志
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Celery 配置
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/4'  # Redis 服务器地址和数据库编号
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/5'  # Redis 存储任务结果

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# (可选) 如果使用时区敏感任务，请启用以下设置
CELERY_TIMEZONE = 'Asia/Shanghai'  # 设置时区

CELERY_BEAT_SCHEDULE = {
    'task_name': {
        'task': 'search.tasks.test',
        'schedule': timedelta(seconds=60),  # 每 60 秒执行一次
    },
    'delete_search_model': {
        'task': 'search.tasks.delete_search_weekly',
        'schedule': timedelta(weeks=1),
    },
    'update_new_works': {
        'task': 'search.tasks.update_new_works',
        'schedule': timedelta(hours=1),
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
