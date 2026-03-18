from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(
        source='assigned_to.username', read_only=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description',
            'assigned_to', 'assigned_to_username',
            'created_by', 'created_by_username',
            'due_date', 'status',
            'completion_report', 'worked_hours',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class TaskUpdateSerializer(serializers.ModelSerializer):


    class Meta:
        model = Task
        fields = ['status', 'completion_report', 'worked_hours']

    def validate(self, data):
        status = data.get('status', self.instance.status if self.instance else None)

        if status == 'completed':
            report = data.get(
                'completion_report',
                self.instance.completion_report if self.instance else None
            )
            hours = data.get(
                'worked_hours',
                self.instance.worked_hours if self.instance else None
            )

            if not report or str(report).strip() == '':
                raise serializers.ValidationError(
                    {"completion_report": "Completion report is required when marking a task as completed."}
                )
            if hours is None:
                raise serializers.ValidationError(
                    {"worked_hours": "Worked hours are required when marking a task as completed."}
                )
            if float(hours) <= 0:
                raise serializers.ValidationError(
                    {"worked_hours": "Worked hours must be greater than 0."}
                )

        return data


class TaskReportSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(
        source='assigned_to.username', read_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'assigned_to_username',
            'status', 'completion_report', 'worked_hours', 'updated_at'
        ]
