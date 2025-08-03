import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Task, TimeRecord


class TaskFilter(django_filters.FilterSet):
    """
    Filters for Task model.
    """
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Description'
    )
    creation_date_start = django_filters.DateFilter(
        field_name='creation_date',
        lookup_expr='gte',
        label='Creation Date (Start)'
    )
    creation_date_end = django_filters.DateFilter(
        field_name='creation_date',
        lookup_expr='lte',
        label='Creation Date (End)'
    )
    active = django_filters.BooleanFilter(
        label='Active Task'
    )
    search = django_filters.CharFilter(
        method='search_filter',
        label='General Search'
    )
    
    class Meta:
        model = Task
        fields = {
            'description': ['exact', 'icontains'],
            'creation_date': ['exact', 'gte', 'lte'],
            'active': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search filter that looks in task description.
        """
        return queryset.filter(
            Q(description__icontains=value) |
            Q(responsible_user__username__icontains=value) |
            Q(responsible_user__first_name__icontains=value) |
            Q(responsible_user__last_name__icontains=value)
        )


class TimeRecordFilter(django_filters.FilterSet):
    """
    Filters for TimeRecord model.
    """
    work_description = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Work Description'
    )
    task_description = django_filters.CharFilter(
        field_name='task__description',
        lookup_expr='icontains',
        label='Task Description'
    )
    record_date_start = django_filters.DateFilter(
        field_name='record_date',
        lookup_expr='gte',
        label='Record Date (Start)'
    )
    record_date_end = django_filters.DateFilter(
        field_name='record_date',
        lookup_expr='lte',
        label='Record Date (End)'
    )
    min_time = django_filters.DurationFilter(
        field_name='worked_time',
        lookup_expr='gte',
        label='Minimum Time'
    )
    max_time = django_filters.DurationFilter(
        field_name='worked_time',
        lookup_expr='lte',
        label='Maximum Time'
    )
    user = django_filters.CharFilter(
        field_name='task__responsible_user__username',
        lookup_expr='icontains',
        label='User'
    )
    period = django_filters.ChoiceFilter(
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
        ],
        method='filter_period',
        label='Period'
    )
    search = django_filters.CharFilter(
        method='search_filter',
        label='General Search'
    )
    
    class Meta:
        model = TimeRecord
        fields = {
            'record_date': ['exact', 'gte', 'lte'],
            'worked_time': ['exact', 'gte', 'lte'],
            'work_description': ['exact', 'icontains'],
            'task__description': ['exact', 'icontains'],
            'task__responsible_user__username': ['exact', 'icontains'],
        }
    
    def filter_period(self, queryset, name, value):
        """
        Filter by predefined period.
        """
        today = timezone.now().date()
        
        if value == 'today':
            return queryset.filter(record_date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(record_date=yesterday)
        elif value == 'this_week':
            week_start = today - timedelta(days=today.weekday())
            return queryset.filter(record_date__gte=week_start)
        elif value == 'last_week':
            week_start = today - timedelta(days=today.weekday() + 7)
            week_end = week_start + timedelta(days=6)
            return queryset.filter(record_date__range=[week_start, week_end])
        elif value == 'this_month':
            month_start = today.replace(day=1)
            return queryset.filter(record_date__gte=month_start)
        elif value == 'last_month':
            if today.month == 1:
                last_month_start = today.replace(year=today.year-1, month=12, day=1)
            else:
                last_month_start = today.replace(month=today.month-1, day=1)
            last_month_end = today.replace(day=1) - timedelta(days=1)
            return queryset.filter(record_date__range=[last_month_start, last_month_end])
        
        return queryset
    
    def search_filter(self, queryset, name, value):
        """
        Search filter that looks in multiple fields.
        """
        return queryset.filter(
            Q(work_description__icontains=value) |
            Q(task__description__icontains=value) |
            Q(task__responsible_user__username__icontains=value) |
            Q(task__responsible_user__first_name__icontains=value) |
            Q(task__responsible_user__last_name__icontains=value) |
            Q(record_date__icontains=value)
        ) 