from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import *
# Create your views here.


@require_POST
def create_tracker(request):
    user_id = request.POST.get('user_id', '')
    tracker_name = request.POST.get('tracker_name', '')
    para = request.POST.get('para', '')
    if user_id == '' or tracker_name == '' or para == '':
        result = {'result': 'error', 'message': '缺少用户id 或 跟踪器名称 或 参数内容'}
        return JsonResponse(result)

    TrackerList.objects.create(user_id=user_id, tracker_name=tracker_name, para=para)
    tracker = TrackerList.objects.filter(user_id=user_id).first()
    tracker_id = tracker.id
    create_time = tracker.create_time
    result = {'result': 'successful',
              'message': '跟踪器建立成功',
              'tracker_id': tracker_id,
              'tracker_name': tracker_name,
              'create_time': create_time}
    return JsonResponse(result)


@require_POST
def delete_tracker(request):
    user_id = request.POST.get('user_id', '')
    tracker_id = request.POST.get('tracker_id', '')

    if user_id == '' or tracker_id == '':
        result = {'result': 'error', 'message': '缺少用户id 或 跟踪器id'}
        return JsonResponse(result)

    tracker = TrackerList.objects.filter(id=tracker_id)
    if not tracker:
        result = {'result': 'error', 'message': '跟踪器不存在或者已经被删除'}
        return JsonResponse(result)
        
    TrackerList.objects.filter(id=tracker_id).delete()

    result = {'result': 'delete successful'}
    return JsonResponse(result)


@require_POST
def get_user_all_trackers(request):
    user_id = request.POST.get('user_id', '')

    if user_id == '':
        result = {'result': 'error', 'message': '缺少用户id'}
        return JsonResponse(result)

    trackers = TrackerList.objects.filter(user_id=user_id)

    trackers_details = [tracker_detail.to_dic() for tracker_detail in trackers]

    result = {'result': 'successful',
              'trackers_details': trackers_details}

    return JsonResponse(result)