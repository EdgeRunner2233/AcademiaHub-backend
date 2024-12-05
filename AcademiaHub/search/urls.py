from django.urls import path
from . import views

urlpatterns = [
    path('search', views.ordinary_search, name='search'),
    path('a', views.a),
]