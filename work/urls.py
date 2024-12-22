from django.urls import path
from . import views

urlpatterns = [
    path('get_update_interval', views.get_update_interval, name='get_update_interval'),
    path('set_update_interval', views.set_update_interval, name='set_update_interval'),
    path('update_dataset', views.update_dataset, name='update_dataset'),
]