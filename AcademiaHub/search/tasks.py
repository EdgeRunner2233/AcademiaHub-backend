# tasks.py
from celery import shared_task
from search.models import *
from AcademiaHub.celery import app
import requests
import logging
from django.core.cache import cache
from utils.search_utils import openAlex_ordinary_search

logger = logging.getLogger('celeryFile')


@app.task
def calculate_statistics(params):
    base_url = "https://api.openalex.org/works"
    # 向 OpenAlex API 发送请求
    params['group_by'] = "publication_year"
    response = requests.get(base_url, params=params)
    data = response.json()
    publication_year_list = data.get('group_by', [])

    params['group_by'] = "type"
    response = requests.get(base_url, params=params)
    data = response.json()
    type_list = data.get('group_by', [])

    params['group_by'] = "author.id"
    response = requests.get(base_url, params=params)
    data = response.json()
    author_list = data.get('group_by', [])

    # 创建统计结果对象并保存到数据库
    stats = Statistics.objects.create(
        filter=params['filter'],
        publication_year_list=publication_year_list,
        type_list=type_list,
        author_list=author_list,
    )

    return {
        'publication_year_list': publication_year_list,
        'type_list': type_list,
        'author_list': author_list,
    }

@app.task
def test():
    logger.info("successful !")

@app.task
def delete_search_weekly():
    SearchWork.objects.all().update(number=0)
    SearchWord.objects.all().update(number=0)