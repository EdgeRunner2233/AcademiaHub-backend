from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
import requests
import os
import random
import environ
# Create your views here.

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

def update_dataset(request):
    # TODO
    print("update dataset !!!")

    result = {'result': "update dataset success !"}
    return JsonResponse(result)

