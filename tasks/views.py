from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Task
from .serializers import TaskSerializer, TaskUpdateSerializer, TaskReportSerializer
from accounts.permissions import IsUser, IsAdminOrSuperAdmin


# ── GET /api/tasks/ ────────────────────────────────────────────────────────────

class TaskListAPIView(APIView):
    """
    GET /api/tasks/
    Returns all tasks assigned to the currently logged-in user.
    Permission: role == 'user' only.
    """
    permission_classes = [IsUser]

    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ── PUT /api/tasks/{id}/ ───────────────────────────────────────────────────────

class TaskUpdateAPIView(APIView):
    """
    PUT /api/tasks/{id}/
    Allows the assigned user to update task status.
    When status == 'completed', completion_report and worked_hours are mandatory.
    Permission: role == 'user' only, and only their own tasks.
    """
    permission_classes = [IsUser]

    def put(self, request, pk):
        task = get_object_or_404(Task, id=pk, assigned_to=request.user)

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Return full task detail after update
            return Response(
                TaskSerializer(task).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── GET /api/tasks/{id}/report/ ────────────────────────────────────────────────

class TaskReportAPIView(APIView):
    """
    GET /api/tasks/{id}/report/
    Returns the completion report and worked hours for a completed task.
    Permission: role == 'admin' or 'superadmin' only.
    Only available for tasks with status == 'completed'.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)

        if task.status != 'completed':
            return Response(
                {"error": "Report is only available for completed tasks."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TaskReportSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
