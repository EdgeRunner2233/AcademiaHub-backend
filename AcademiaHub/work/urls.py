from django.urls import path
from . import views

urlpatterns = [
    path('download-work-pdf', views.download_work_pdf, name='download-work-pdf'),
]