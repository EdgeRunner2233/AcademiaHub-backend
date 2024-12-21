from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from collections import defaultdict
from .models import *
from utils.search_utils import *

# Create your views here.

@require_POST
def create_mark_list(request):
    user_id = request.POST.get('user_id', '')
    list_name = request.POST.get('list_name', '')
    description = request.POST.get('description', '')

    if user_id == '' or list_name == '':
        result = {'result': 'error', 'message': '缺少用户id 或 标记列表名称'}
        return JsonResponse(result)
    marks = Mark.objects.filter(user_id=user_id, list_name=list_name)
    if marks.exists():
        result = {'result': 'error', 'massage': '标记列表已存在'}
        return JsonResponse(result)
    mark = Mark.objects.create(user_id=user_id, list_name=list_name, description=description)

    result = {'result': 'successful', 'message': '标记列表建立成功', 'id': mark.id, 'list_name': list_name, 'description': description}
    return JsonResponse(result)

@require_POST
def modify_description(request):
    user_id = request.POST.get('user_id', '')
    list_id = request.POST.get('list_id', '')
    description = request.POST.get('description', '')

    if user_id == '' or list_id == '':
        result = {'result': 'error', 'message': '缺少用户id 或 标记列表名称'}
        return JsonResponse(result)
    mark = Mark.objects.filter(id=list_id).first()
    if not mark:
        result = {'result': 'error', 'massage': '标记列表不存在'}
        return JsonResponse(result)

    mark.description = description
    mark.save()
    result = {'result': 'successful', 'message': '更改描述成功'}
    return JsonResponse(result)



@require_POST
def add_mark(request):
    user_id = request.POST.get('user_id', '')
    list_id = request.POST.get('list_id', '')
    work_id = request.POST.get('work_id', '')

    if user_id == '' or list_id == '' or work_id == '':
        result = {'result': 'error', 'message': '缺少用户id 或 标记列表名称 或 文献id'}
        return JsonResponse(result)

    mark = Mark.objects.get(id=list_id)
    if mark is None:
        result = {'result': 'error', 'massage': '标记列表不存在'}
        return JsonResponse(result)

    mark.count += 1  
    mark.save()  

    mark_relationships = MarkRelationships.objects.filter(mark_list=mark, work_id=work_id)
    if mark_relationships:
        result = {'result': 'error', 'massage': '已添加到标记列表中'}
        return JsonResponse(result)

    mark_relationship = MarkRelationships.objects.create(mark_list=mark, work_id=work_id)
    result = {'result': 'successful', 'message': '添加成功', 'id': mark_relationship.id, 'mark_list_id': mark.id, 'work_id': work_id}
    return JsonResponse(result)

@require_POST
def get_user_marks(request):
    user_id = request.POST.get('user_id', '')

    if user_id == '':
        result = {'result': 'error', 'message': '缺少用户id'}
        return JsonResponse(result)

    marks = Mark.objects.filter(user_id=user_id).prefetch_related(
        Prefetch('mark_list', queryset=MarkRelationships.objects.all())
    )

    if not marks:
        result = {'result': 'error', 'message': '该用户没有标记列表'}
        return JsonResponse(result)

    user_marks_with_details = []

    for mark in marks:
        mark_relationships = MarkRelationships.objects.filter(mark_list=mark)

        topics_dict = defaultdict(list)

        work_ids = [relationship.to_dic() for relationship in mark_relationships]

        for mark_relationship in mark_relationships:
            work = get_single_work(mark_relationship.work_id)
            topics = work.get('topics', [])

            for topic in topics:
                topic_id = topic['id']
                topic_name = topic['display_name']

                topics_dict[topic_name].append({
                    'id': mark_relationship.id,
                    'work_id': work['id'],
                    'title': work['title'],
                    'doi': work['doi'],
                    'publication_year': work['publication_year'],
                    'authors': [author['author']['display_name'] for author in work['authorships']]
                })

        user_marks_with_details.append({
            'mark_list_id': mark.id,
            'list_name': mark.list_name,
            'description': mark.description,
            'topics_dict': topics_dict,
        })

    result = {
        'result': 'successful',
        'message': '获取成功',
        'user_marks': user_marks_with_details
    }
    return JsonResponse(result)

@require_POST
def get_user_single_mark_list(request):
    user_id = request.POST.get('user_id', '')
    list_id = request.POST.get('list_id', '')

    if user_id == '':
        result = {'result': 'error', 'message': '缺少用户id'}
        return JsonResponse(result)

    marks = Mark.objects.filter(id=list_id).prefetch_related(
        Prefetch('mark_list', queryset=MarkRelationships.objects.all())
    )

    if not marks:
        result = {'result': 'error', 'message': '该用户没有标记列表'}
        return JsonResponse(result)

    user_marks_with_details = []

    for mark in marks:
        mark_relationships = MarkRelationships.objects.filter(mark_list=mark)

        topics_dict = defaultdict(list)

        work_ids = [relationship.work_id for relationship in mark_relationships]

        for work_id in work_ids:
            work = get_single_work(work_id)
            topics = work.get('topics', [])

            for topic in topics:
                topic_id = topic['id']
                topic_name = topic['display_name']

                topics_dict[topic_name].append({
                    'id': work['id'],
                    'title': work['title'],
                    'doi': work['doi'],
                    'publication_year': work['publication_year'],
                    'authors': [author['author']['display_name'] for author in work['authorships']]
                })

        topics_dict_with_num = {
            topic_name: {
                'num': len(topic_list),  # Add count of works for each topic
                'works': topic_list       # Keep the list of works under 'works'
            }
            for topic_name, topic_list in topics_dict.items()
        }

        user_marks_with_details.append({
            'mark_list_id': mark.id,
            'count': mark.count,
            'list_name': mark.list_name,
            'description': mark.description,
            'topics_dict': topics_dict_with_num,
        })

    result = {
        'result': 'successful',
        'message': '获取成功',
        'user_marks': user_marks_with_details,
    }
    return JsonResponse(result)


@require_POST
def get_user_mark_lists(request):
    user_id = request.POST.get('user_id', '')

    if user_id == '':
        result = {'result': 'error', 'message': '缺少用户id'}
        return JsonResponse(result)

    marks = Mark.objects.filter(user_id=user_id)
    marks_data = [mark.to_dic() for mark in marks]
    count = len(marks_data)
    result = {'result': 'successful', 'count': count, 'markLists': marks_data}
    return JsonResponse(result)

@require_POST
def delete_mark_relationship(request):
    user_id = request.POST.get('user_id', '')
    mark_relationship_id = request.POST.get('mark_relationship_id', '')

    if user_id == '' or mark_relationship_id == '':
        result = {'result': 'error', 'message': '缺少用户id 或 标记id'}
        return JsonResponse(result)

    mark_relationship = MarkRelationships.objects.filter(id=mark_relationship_id).first()
    if not mark_relationship:
        result = {'result': 'error', 'message': '标记id不存在'}
        return JsonResponse(result)

    mark_relationship.delete()
    result = {'result': 'successful', 'message': 'MarkRelationship deleted successfully'}
    return JsonResponse(result)


@require_POST
def delete_mark(request):
    user_id = request.POST.get('user_id', '')
    mark_id = request.POST.get('mark_id', '')

    if user_id == '' or mark_id == '':
        result = {'result': 'error', 'message': '缺少用户id 或 标记列表id'}
        return JsonResponse(result)

    mark = Mark.objects.filter(id=mark_id).first()
    if not mark:
        result = {'result': 'error', 'message': '标记列表id不存在'}
        return JsonResponse(result)

    mark.delete()
    result = {'result': 'successful', 'message': 'Mark deleted successfully'}
    return JsonResponse(result)

@require_POST
def get_user_single_mark_list_detail(request):
    user_id = request.POST.get('user_id', '')
    list_id = request.POST.get('list_id', '')

    if user_id == '':
        result = {'result': 'error', 'message': '缺少用户id'}
        return JsonResponse(result)

    try:
        # 查找 Mark 对象
        mark = Mark.objects.get(id=list_id)
    except Mark.DoesNotExist:
        return JsonResponse({'result': 'error', 'message': '该用户没有标记列表'})

    mark_relationships = MarkRelationships.objects.filter(mark_list=mark)

    result = {
        'mark_info': mark.to_dic(),  # Mark 信息
        'relationships': [relationship.to_dic() for relationship in mark_relationships]  # MarkRelationships 信息
    }

    return JsonResponse(result)
