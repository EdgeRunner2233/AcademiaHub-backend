import json
import time
from diophila import OpenAlex, openalex
from django.core.cache import cache
from AcademiaHub.settings import env
import logging
import concurrent.futures
import asyncio
import aiohttp
from asyncio import TimeoutError

logger = logging.getLogger('mylogger')
openalex = OpenAlex("15129275190@163.com")

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


async def fetch_work_details(work, index, works_detail, session):
    try:
        continuesingle_work = cache.get("https://openalex.org/"+work)
        if continuesingle_work:
            continuesingle_work = json.loads(continuesingle_work)
            works_detail.append({
                'index': index,
                'work_id': continuesingle_work.get('id'),
                'work_title': continuesingle_work.get('title'),
                'author_name': continuesingle_work['author_name'],
                'cited_by_count': continuesingle_work.get('cited_by_count'),
                'publication_date': continuesingle_work.get('publication_date'),
                'source':continuesingle_work.get('primary_location').get('source').get('display_name')
            })
        else:
            # 设置aiohttp超时
            timeout = aiohttp.ClientTimeout(total=10)  # 设置10秒总超时
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"https://api.openalex.org/works/{work}") as response:
                    if response.status == 200:
                        single_work = await response.json()
                        authorships = single_work.get('authorships', [])
                        author_name = ', '.join(author_entry['author']['display_name'] for author_entry in authorships)
                        single_work['author_name'] = author_name
                        works_detail.append({
                            'index': index,
                            'work_id': single_work.get('id'),
                            'work_title': single_work.get('title'),
                            'author_name': single_work['author_name'],
                            'cited_by_count': single_work.get('cited_by_count'),
                            'publication_date': single_work.get('publication_date'),
                            'source':single_work.get('primary_location').get('source').get('display_name')
                        })
                    else:
                        print(f"Error: {response.status} for work {work}")
    except asyncio.TimeoutError:
        print(f"Request for work {work} timed out.")
    except Exception as e:
        print(f"Error fetching work details for {work}: {e}")

async def get_work_details(works):
    works_detail = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_work_details(work.split('/')[-1], index, works_detail, session) for index, work in enumerate(works[:6], 1)]
        await asyncio.gather(*tasks)
    return works_detail

# def get_work_details(works):
#     works_detail = []

#     def fetch_work_details(work, index):
#         try:
#             continuesingle_work = cache.get(work)
#             if continuesingle_work:
#                 works_detail.append({
#                     'index': index,
#                     'work_id': continuesingle_work.get('id'),
#                     'work_title': continuesingle_work.get('title'),
#                     'author_name': continuesingle_work['author_name'],
#                     'cited_by_count': continuesingle_work.get('cited_by_count'),
#                     'publication_date': continuesingle_work.get('publication_date'),
#                 })
#             else:
#                 time.sleep(1)  # If needed, add a small delay between requests
#                 single_work = openalex.get_single_work(work, 'openalex')
#                 authorships = single_work.get('authorships', [])
#                 author_name = ', '.join(author_entry['author']['display_name'] for author_entry in authorships)
#                 single_work['author_name'] = author_name
#                 works_detail.append({
#                     'index': index,
#                     'work_id': single_work.get('id'),
#                     'work_title': single_work.get('title'),
#                     'author_name': single_work['author_name'],
#                     'cited_by_count': single_work.get('cited_by_count'),
#                     'publication_date': single_work.get('publication_date'),
#                 })
#         except Exception as e:
#             print(f"Error fetching work details for {work}: {e}")

#     # Using ThreadPoolExecutor to fetch work details concurrently
#     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#         # Create a list of futures for each work
#         futures = [executor.submit(fetch_work_details, work, index) for index, work in enumerate(works[:2], 1)]
#         # Wait for all futures to complete
#         concurrent.futures.wait(futures)
    
#     return works_detail

            


def get_single_work(openalex_id):
    single_work = cache.get(openalex_id)
    if single_work is None:
        single_work = openalex.get_single_work(openalex_id,'openalex')

        single_work['abstract'] = ''
        if single_work['abstract_inverted_index'] is not None:
            single_work['abstract'] = get_abstract(single_work['abstract_inverted_index'])

        authorships = single_work['authorships']
        institutions_info = []
        #author_name = ', '.join(author_entry['author']['display_name'] for author_entry in authorships)
        #single_work['author_name'] = author_name

        for author_entry in authorships:
            for institution in author_entry['institutions']:
                institutions_info.append({
                    "id": institution['id'],
                    "display_name": institution['display_name']
                })

        single_work['institutions_info'] = institutions_info
        # single_work['referenced_works_detail'] = get_work_details(single_work['referenced_works'])
        #single_work['related_works_detail'] = get_work_details(single_work['related_works'])

        key = single_work['id']
        value = single_work
        cache.set(key, value, timeout=300)
    return single_work

# 获取最近被收录的150篇文章
def get_new150_works():
    filters = None  # 可以根据需要设置过滤器
    search = None  # 如果没有搜索条件
    sort = {'publication_date': 'desc'}  # 按照发布日期降序排列（'asc' 或 'desc'）
    per_page = 150
    pages = [1]  # 获取第一页的结果

    value = list(openalex.get_list_of_works(filters=filters, search=search, sort=sort, per_page=per_page, pages=pages))
    return value