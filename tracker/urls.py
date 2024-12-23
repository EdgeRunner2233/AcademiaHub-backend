from django.urls import path
from . import views

urlpatterns = [
    path('create-tracker', views.create_tracker, name='create-tracker'),
    path('delete-tracker', views.delete_tracker, name='delete-tracker'),
    path('get-user-all-trackers', views.get_user_all_trackers, name='get-user-all-trackers'),
]