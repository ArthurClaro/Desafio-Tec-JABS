from django.urls import path
from . import web_views

app_name = 'time_tracking'

urlpatterns = [
    # Dashboard
    path('', web_views.dashboard, name='dashboard'),
    
    # Tasks
    path('tasks/', web_views.task_list, name='task_list'),
    path('tasks/new/', web_views.new_task, name='new_task'),
    path('tasks/<int:pk>/', web_views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', web_views.edit_task, name='edit_task'),
    
    # Time Records
    path('records/', web_views.record_list, name='record_list'),
    path('records/new/', web_views.new_record, name='new_record'),
    path('records/<int:pk>/edit/', web_views.edit_record, name='edit_record'),
] 