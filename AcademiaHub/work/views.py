from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
import requests
import os
import random

# Create your views here.

@require_POST
def download_work_pdf(request):
    work_id = request.POST.get('work_id', '')
    pdf_url = request.POST.get('pdf_url', '')
    if not work_id:
        return JsonResponse({'result': 'error'})

    return JsonResponse(result)


