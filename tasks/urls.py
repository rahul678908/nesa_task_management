from django.urls import path
from .views import TaskListAPIView, TaskUpdateAPIView, TaskReportAPIView

urlpatterns = [
    path('', TaskListAPIView.as_view(), name='task-list'),
    path('<int:pk>/', TaskUpdateAPIView.as_view(), name='task-update'),
    path('<int:pk>/report/', TaskReportAPIView.as_view(), name='task-report'),
]
