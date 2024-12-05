from django.http import JsonResponse
from django.views.decorators.http import require_POST

from utils.search_utils import openAlex_ordinary_search


# Create your views here.
@require_POST
def ordinary_search(request):
    text = request.POST.get('key', '')
    type = request.POST.get('type', '') # 1: 作者 2: 文献
    page = request.POST.get('page', '')
    value = openAlex_ordinary_search(text, type, page)

    result = {'type': type, 'result': value}

    return JsonResponse(result)

@require_POST
def a(request):
    result = {'type': 1}
    return JsonResponse(result)