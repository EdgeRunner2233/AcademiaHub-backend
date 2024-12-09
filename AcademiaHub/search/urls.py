from django.urls import path
from . import views

urlpatterns = [
    path('search', views.ordinary_search, name='search'),
    path('advanced_search', views.advanced_search, name='advanced_search'),
    
    path('single-work', views.get_specific_work, name='single_work'),

    path('hot-paper', views.get_weekly_popular_works, name='hot-paper'),
    path('hot-word', views.get_weekly_popular_words, name='hot-word'),
    path('new-paper', views.get_new_works, name='new-paper'),

    path('your_view', views.your_view, name='your_view'),

]