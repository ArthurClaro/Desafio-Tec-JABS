from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, TimeRecord


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    
    responsible_user = UserSerializer(read_only=True)
    total_worked_time = serializers.SerializerMethodField()
    total_hours = serializers.SerializerMethodField()
    records_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'responsible_user', 'creation_date', 'description', 
            'active', 'total_worked_time', 'total_hours', 'records_count'
        ]
        read_only_fields = ['id', 'responsible_user', 'creation_date']
    
    def get_total_worked_time(self, obj):
        """Returns total worked time in seconds."""
        total = obj.total_worked_time
        return total.total_seconds() if total else 0
    
    def get_total_hours(self, obj):
        """Returns total hours formatted."""
        return obj.total_hours
    
    def get_records_count(self, obj):
        """Returns number of time records."""
        return obj.time_records.count()
    
    def create(self, validated_data):
        """Creates a new task associated with current user."""
        validated_data['responsible_user'] = self.context['request'].user
        return super().create(validated_data)


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for task creation."""
    
    class Meta:
        model = Task
        fields = ['description', 'active']
    
    def create(self, validated_data):
        """Creates a new task associated with current user."""
        validated_data['responsible_user'] = self.context['request'].user
        return super().create(validated_data)


class TimeRecordSerializer(serializers.ModelSerializer):
    """Serializer for TimeRecord model."""
    
    task = TaskSerializer(read_only=True)
    task_id = serializers.IntegerField(write_only=True)
    worked_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeRecord
        fields = [
            'id', 'task', 'task_id', 'record_date', 'worked_time',
            'work_description', 'creation_date', 'worked_hours'
        ]
        read_only_fields = ['id', 'creation_date']
    
    def get_worked_hours(self, obj):
        """Returns worked hours formatted."""
        return obj.worked_hours
    
    def validate_task_id(self, value):
        """Validates if task exists and belongs to current user."""
        user = self.context['request'].user
        try:
            task = Task.objects.get(id=value, responsible_user=user)
            return value
        except Task.DoesNotExist:
            raise serializers.ValidationError(
                "Task not found or you don't have permission to access it."
            )
    
    def create(self, validated_data):
        """Creates a new time record."""
        task_id = validated_data.pop('task_id')
        validated_data['task_id'] = task_id
        return super().create(validated_data)


class TimeRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for time record creation."""
    
    task_id = serializers.IntegerField()
    
    class Meta:
        model = TimeRecord
        fields = ['task_id', 'record_date', 'worked_time', 'work_description']
    
    def validate_task_id(self, value):
        """Validates if task exists and belongs to current user."""
        user = self.context['request'].user
        try:
            task = Task.objects.get(id=value, responsible_user=user)
            return value
        except Task.DoesNotExist:
            raise serializers.ValidationError(
                "Task not found or you don't have permission to access it."
            )
    
    def create(self, validated_data):
        """Creates a new time record."""
        task_id = validated_data.pop('task_id')
        validated_data['task_id'] = task_id
        return super().create(validated_data)


class TaskDetailSerializer(TaskSerializer):
    """Detailed serializer for tasks including time records."""
    
    time_records = TimeRecordSerializer(many=True, read_only=True)
    
    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['time_records']


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard data."""
    
    total_tasks = serializers.IntegerField()
    active_tasks = serializers.IntegerField()
    total_worked_hours = serializers.FloatField()
    hours_this_week = serializers.FloatField()
    hours_this_month = serializers.FloatField()
    recent_tasks = serializers.ListField()
    recent_records = serializers.ListField() 