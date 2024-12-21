from django.urls import path
from . import views

urlpatterns = [
    path('create-mark-list', views.create_mark_list, name='create-mark-list'),
    path('modify-description', views.modify_description, name='modify-description'),
    path('add-mark', views.add_mark, name='add-mark'),
    path('get-user-marks', views.get_user_marks, name='get-user-marks'),
    path('get-user-single-mark-list', views.get_user_single_mark_list, name='get-user-single-mark-list'),
    path('get-user-single-mark-list-detail', views.get_user_single_mark_list_detail, name='get-user-single-mark-list-detail'),
    path('get-user-mark-lists', views.get_user_mark_lists, name='get-user-mark-lists'),
    path('delete-mark-relationship', views.delete_mark_relationship, name='delete-mark-relationship'),
    path('delete-mark', views.delete_mark, name='delete-mark'),
]