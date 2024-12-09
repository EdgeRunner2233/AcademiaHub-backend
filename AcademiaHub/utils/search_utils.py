import json

from diophila import OpenAlex, openalex
from django.core.cache import cache
from AcademiaHub.settings import env
import logging

logger = logging.getLogger('mylogger')
openalex = OpenAlex()
def openAlex_ordinary_search(text, type, page):
    # cache.clear()
    request_dir = {
        'text': text,
        'type': type,
        'page': page,
    }
    key = json.dumps(request_dir)
    value = cache.get(key)
    page = int(page)
    if type == '1':
        if value is None:
            value = list(openalex.get_list_of_authors(filters=None,
                                                      search=text,
                                                      sort=None,
                                                      per_page=25,
                                                      pages=[page]))
    if type == '0':
        if value is None:
            value = list(openalex.get_list_of_works(filters={"is_oa": "true"},
                                                      search=text,
                                                      sort=None,
                                                      per_page=25,
                                                      pages=[page]))
            for work in value[0]['results']:
                if work['abstract_inverted_index'] is not None:
                    work['abstract'] = get_abstract(work['abstract_inverted_index'])
                else :
                    work['abstract'] = ''


    cache.set(key, value, timeout=300)
    return value

def get_abstract(abstract_inverted_index):
    abstract = []
    for key, value in abstract_inverted_index.items():
        for value_i in value:
            abstract.insert(value_i, key)

    abstract = ' '.join(abstract)
    return abstract

def get_single_work(openalex_id):
    single_work = cache.get(openalex_id)
    if single_work is None:
        single_work = openalex.get_single_work(openalex_id)

        key = single_work['id']
        value = single_work
        cache.set(key, value, timeout=300)
    return single_work

# 获取最近被收录的10篇文章
def get_new10_works():
    filters = None  # 可以根据需要设置过滤器
    search = None  # 如果没有搜索条件
    sort = {'publication_date': 'desc'}  # 按照发布日期降序排列（'asc' 或 'desc'）
    per_page = 10  # 每页 10 个工作项
    pages = [1]  # 获取第一页的结果

    new10_works = list(openalex.get_list_of_works(filters=filters, search=search, sort=sort, per_page=per_page, pages=pages))
    return new10_works
