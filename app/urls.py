from django.urls import path
from . import views

app_name = "app"
urlpatterns = [
    path("", views.index, name="index"),
    path('load-task/', views.load_task, name='load_task'),
    path('task_details', views.task_details, name='task_details'),
    path('send_message/', views.send_message, name='send_message'),
]