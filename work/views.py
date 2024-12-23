from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
import requests
import os
import random
import environ
# Create your views here.

from search.tasks import *

env = environ.Env()
environ.Env.read_env(env_file='/AcademiaHub/Backend/AcademiaHub/.env')

def set_update_interval(request):
    update_interval = request.POST.get('interval', '') 

    with open('/AcademiaHub/Backend/AcademiaHub/.env', 'r') as f:
        lines = f.readlines()

    with open('/AcademiaHub/Backend/AcademiaHub/.env', 'w') as f:
        found = False
        for line in lines:
            if line.startswith('UPDATE_INTERVAL'):
                f.write(f'UPDATE_INTERVAL={update_interval}\n')  # 写入新的值
                found = True
            else:
                f.write(line)

        # 如果没有找到指定的键，追加一个新的键值对
        if not found:
            f.write(f'UPDATE_INTERVAL={update_interval}\n')

    result = {'result': "set update_interval success !"}
    return JsonResponse(result)


def get_update_interval(request):
    update_interval = env('UPDATE_INTERVAL') 

    result = {'result': "get update_interval success !",'update_interval': update_interval}
    return JsonResponse(result)

@require_POST
def update_dataset(request):
    # TODO
    update_dataset_task()

    result = {'result': "update dataset success !"}
    return JsonResponse(result)

@require_POST
def update_dataset(request):
    # TODO
    update_dataset_task()

    result = {'result': "update dataset success !"}
    return JsonResponse(result)

@require_POST
def get_recent_counts(request):
    # 获取最近五条文献总量记录，按ID降序排列
    recent_records = TotalLiteratureCount.objects.all().order_by('-id')[:5]
    
    # 提取文献总量字段
    total_literature_counts = [record.total_literature_count for record in recent_records]
    
    # 返回一个包含最近五次文献总量的列表
    return JsonResponse({'recent_literature_counts': total_literature_counts})
