from django.urls import path
from . import views

urlpatterns = [
    path('search', views.ordinary_search, name='search'),
    path('advanced_search', views.advanced_search, name='advanced_search'),
    path('a', views.a),
]