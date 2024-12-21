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
def test():
    logger.info("successful !")

@app.task
def calculate_statistics(params):
    # 检查是否已经存在相同的filter记录
    existing_stats = Statistics.objects.filter(filter=params['filter']).first()
    if existing_stats:
        # 如果记录已经存在，直接返回已有的数据
        return {
            'publication_year_list': existing_stats.publication_year_list,
            'type_list': existing_stats.type_list,
            'author_list': existing_stats.author_list,
        }

    # 如果记录不存在，继续抓取数据
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

    # 创建新的统计记录
    stats = Statistics.objects.update_or_create(
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