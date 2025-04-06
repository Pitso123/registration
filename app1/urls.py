from django.urls import path
from .views import schedule_view, add_schedule, delete_schedule

urlpatterns = [
    path('schedule/', schedule_view, name='schedule'),
    path('schedule/add/', add_schedule, name='add_schedule'),
    path('schedule/delete/<int:schedule_id>/', delete_schedule, name='delete_schedule'),
]