from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Task, TimeRecord
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskDetailSerializer,
    TimeRecordSerializer, TimeRecordCreateSerializer, DashboardSerializer
)
from .filters import TaskFilter, TimeRecordFilter


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    """
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = TaskFilter
    search_fields = ['description']
    ordering_fields = ['creation_date', 'description']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Returns only tasks from authenticated user."""
        return Task.objects.filter(responsible_user=self.request.user)
    
    def get_serializer_class(self):
        """Returns appropriate serializer based on action."""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Automatically associates current user to task."""
        serializer.save(responsible_user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggles task status between active and inactive."""
        task = self.get_object()
        task.active = not task.active
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False)
    def active(self, request):
        """Lists only active tasks."""
        tasks = self.get_queryset().filter(active=True)
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def inactive(self, request):
        """Lists only inactive tasks."""
        tasks = self.get_queryset().filter(active=False)
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class TimeRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing time records.
    """
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = TimeRecordFilter
    search_fields = ['work_description', 'task__description']
    ordering_fields = ['record_date', 'worked_time', 'creation_date']
    ordering = ['-record_date', '-creation_date']
    
    def get_queryset(self):
        """Returns only time records from authenticated user."""
        return TimeRecord.objects.filter(task__responsible_user=self.request.user)
    
    def get_serializer_class(self):
        """Returns appropriate serializer based on action."""
        if self.action == 'create':
            return TimeRecordCreateSerializer
        return TimeRecordSerializer
    
    @action(detail=False)
    def today(self, request):
        """Lists time records from today."""
        today = timezone.now().date()
        records = self.get_queryset().filter(record_date=today)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def this_week(self, request):
        """Lists time records from this week."""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        records = self.get_queryset().filter(record_date__gte=week_start)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def this_month(self, request):
        """Lists time records from this month."""
        today = timezone.now().date()
        month_start = today.replace(day=1)
        records = self.get_queryset().filter(record_date__gte=month_start)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def summary(self, request):
        """Returns a summary of time records."""
        records = self.get_queryset()
        
        # Total worked hours
        total_hours = records.aggregate(
            total=Sum('worked_time')
        )['total'] or timedelta(0)
        
        # Hours this week
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_hours = records.filter(record_date__gte=week_start).aggregate(
            total=Sum('worked_time')
        )['total'] or timedelta(0)
        
        # Hours this month
        month_start = today.replace(day=1)
        month_hours = records.filter(record_date__gte=month_start).aggregate(
            total=Sum('worked_time')
        )['total'] or timedelta(0)
        
        return Response({
            'total_hours': total_hours.total_seconds() / 3600,
            'week_hours': week_hours.total_seconds() / 3600,
            'month_hours': month_hours.total_seconds() / 3600,
            'total_records': records.count(),
        })


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard data.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Returns data for dashboard."""
        user = request.user
        
        # Task statistics
        tasks = Task.objects.filter(responsible_user=user)
        total_tasks = tasks.count()
        active_tasks = tasks.filter(active=True).count()
        
        # Time statistics
        records = TimeRecord.objects.filter(task__responsible_user=user)
        total_hours = records.aggregate(
            total=Sum('worked_time')
        )['total'] or timedelta(0)
        
        # Hours this week
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_hours = records.filter(record_date__gte=week_start).aggregate(
            total=Sum('worked_time')
        )['total'] or timedelta(0)
        
        # Hours this month
        month_start = today.replace(day=1)
        month_hours = records.filter(record_date__gte=month_start).aggregate(
            total=Sum('worked_time')
        )['total'] or timedelta(0)
        
        # Recent data
        recent_tasks = tasks.order_by('-creation_date')[:5]
        recent_records = records.order_by('-creation_date')[:10]
        
        data = {
            'total_tasks': total_tasks,
            'active_tasks': active_tasks,
            'total_worked_hours': total_hours.total_seconds() / 3600,
            'hours_this_week': week_hours.total_seconds() / 3600,
            'hours_this_month': month_hours.total_seconds() / 3600,
            'recent_tasks': TaskSerializer(recent_tasks, many=True).data,
            'recent_records': TimeRecordSerializer(recent_records, many=True).data,
        }
        
        serializer = DashboardSerializer(data)
        return Response(serializer.data)
