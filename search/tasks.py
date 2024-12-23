# tasks.py
from celery import shared_task
from search.models import *
from tracker.models import *
from AcademiaHub.celery import app
import requests
import logging
from django.core.cache import cache
from utils.search_utils import openAlex_ordinary_search
from work.models import *
from faker import Faker
import random

logger = logging.getLogger('celeryFile')
fake = Faker()

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

# 创建模拟文献数据
def generate_literature_data():
    return {
        "title": fake.sentence(nb_words=random.randint(5, 12)),
        "authors": fake.name() + ", " + fake.name(),
        "abstract": fake.text(max_nb_chars=200),
        "publish_text": fake.company(),
        "year": random.randint(1990, 2024),
        "publish": fake.company_suffix(),
        "ref_wr": random.randint(1, 100),
        "key_words": ', '.join([fake.word() for _ in range(random.randint(3, 8))])
    }


# 批量生成数据并存入数据库
def bulk_create_literature(num_entries=10000):
    literature_list = []
    for _ in range(num_entries):
        literature_data = generate_literature_data()
        literature = Literature(**literature_data)
        literature_list.append(literature)

    Literature.objects.bulk_create(literature_list)

def create_total_literature_count():
    # 获取当前模型对象的最新 total_literature_count
    latest = TotalLiteratureCount.objects.latest('id') if TotalLiteratureCount.objects.exists() else None
    if latest:
        # 从最新的total_literature_count基础上增加100-1000的随机数
        increment = random.randint(100, 1000)
        new_count = latest.total_literature_count + increment
    else:
        # 如果没有数据，则从0开始
        increment = random.randint(100, 1000)
        new_count = increment
    
    # 创建并保存新对象
    new_record = TotalLiteratureCount(total_literature_count=new_count)
    new_record.save()
    return increment

@app.task
def update_dataset_task():
    # TODO
    random_objects = TrackerList.objects.all().order_by('?')[:5]
    for tracker in random_objects:
        user_id = tracker.user_id
        body = '您存储的跟踪器 "' + tracker.tracker_name + '" 的搜索内容更新，请查收!'
        requests.post(
            "http://113.44.139.65/api/email/send",
            data={
                "recipient": user_id,
                "subject": "跟踪器修改提醒",
                "body": body,
            },
        )

    new_count = create_total_literature_count()
    bulk_create_literature(new_count)
    logger.info("update dataset !!!")