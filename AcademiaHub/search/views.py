from django.http import JsonResponse
from django.views.decorators.http import require_POST

from utils.search_utils import *
from .models import *
import threading
import logging


logger = logging.getLogger('mylogger')

# Create your views here.
def add_search_word_num(words):
    def task():
        word = words.strip('"')
        word = word.lower()
        word_new, created = SearchWord.objects.get_or_create(
            word=word,
            defaults={'number': 1}  # 新记录时赋值
        )

        if not created:
            word_new.number += 1
            word_new.save()

    threading.Thread(target=task).start()

# 普通搜索
@require_POST
def ordinary_search(request):
    logger.info("ordinary_search")
    text = request.POST.get('key', '')
    type = request.POST.get('type', '') # 1: 作者 2: 文献
    page = request.POST.get('page', '')
    value = openAlex_ordinary_search(text, type, page)

    if type == '0':
        # 将词条存入search-word
        add_search_word_num(text)

    result = {'type': type, 'result': value}

    return JsonResponse(result)


def get_top10_searches():
    top_searches = SearchWork.objects.all().order_by('-number')[:10]
    return [search.to_dic() for search in top_searches]

# 周热门搜索文章
@require_POST
def get_weekly_popular_works(request):
    result = {'result': get_top10_searches()}
    return JsonResponse(result)

def add_search_work_num(work_id, work_title):
    def task():
        work, created = SearchWork.objects.get_or_create(
            work_id=work_id,
            defaults={'work_title': work_title, 'number': 1}  # 新记录时赋值
        )

        if not created:
            work.number += 1
            work.save()

    threading.Thread(target=task).start()


# 获得特定的文章
@require_POST
def get_specific_work(request):
    openalex_id = request.POST.get('openalex_id', '')
    specific_work = get_single_work(openalex_id)
    work_id = specific_work['id']
    work_title = specific_work['title']
    specific_work['pdf'] = None
    for location in specific_work['locations']:
        pdf_url = location.get("pdf_url")
        if pdf_url is not None:
            specific_work['pdf'] = pdf_url
            break

    add_search_work_num(work_id, work_title)

    result = {'result': specific_work}
    return JsonResponse(result)

def get_top10_words():
    top_words = SearchWord.objects.all().order_by('-number')[:10]
    return [words.to_dic() for words in top_words]

# 周热门搜索词条
@require_POST
def get_weekly_popular_words(request):
    result = {'result': get_top10_words()}
    return JsonResponse(result)

@require_POST
def get_new_works(request):
    result = {'result': get_new10_works()}
    return JsonResponse(result)