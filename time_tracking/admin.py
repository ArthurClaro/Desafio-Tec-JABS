from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Task, TimeRecord


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin for Task model."""
    
    list_display = [
        'short_description', 'responsible_user', 'creation_date', 
        'active_status', 'total_time', 'records_count'
    ]
    list_filter = [
        'responsible_user', 'creation_date', 'active'
    ]
    search_fields = [
        'description', 'responsible_user__username', 
        'responsible_user__first_name', 'responsible_user__last_name'
    ]
    readonly_fields = ['creation_date']
    date_hierarchy = 'creation_date'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('responsible_user', 'description', 'active')
        }),
        ('Dates', {
            'fields': ('creation_date',),
            'classes': ('collapse',)
        }),
    )
    
    def short_description(self, obj):
        """Returns a short version of the description."""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    short_description.short_description = 'Description'
    
    def active_status(self, obj):
        """Shows task status with colors."""
        if obj.active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
        )
    active_status.short_description = 'Status'
    
    def total_time(self, obj):
        """Shows total worked time."""
        return obj.total_hours
    total_time.short_description = 'Total Time'
    
    def records_count(self, obj):
        """Shows number of records with link."""
        count = obj.time_records.count()
        url = reverse('admin:time_tracking_timerecord_changelist') + f'?task__id__exact={obj.id}'
        return format_html('<a href="{}">{} records</a>', url, count)
    records_count.short_description = 'Records'
    
    def get_queryset(self, request):
        """Optimizes query with select_related."""
        return super().get_queryset(request).select_related('responsible_user')


@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    """Admin for TimeRecord model."""
    
    list_display = [
        'short_task', 'user', 'record_date', 'formatted_time',
        'short_work_description', 'creation_date'
    ]
    list_filter = [
        'record_date', 'task__responsible_user', 'task__active'
    ]
    search_fields = [
        'work_description', 'task__description', 
        'task__responsible_user__username'
    ]
    readonly_fields = ['creation_date']
    date_hierarchy = 'record_date'
    list_per_page = 25
    
    fieldsets = (
        ('Record Information', {
            'fields': ('task', 'record_date', 'worked_time', 'work_description')
        }),
        ('Metadata', {
            'fields': ('creation_date',),
            'classes': ('collapse',)
        }),
    )
    
    def short_task(self, obj):
        """Returns a short version of task description."""
        description = obj.task.description
        return description[:30] + '...' if len(description) > 30 else description
    short_task.short_description = 'Task'
    
    def user(self, obj):
        """Shows the user responsible for the task."""
        return obj.task.responsible_user.username
    user.short_description = 'User'
    
    def formatted_time(self, obj):
        """Shows formatted time."""
        return obj.worked_hours
    formatted_time.short_description = 'Time'
    
    def short_work_description(self, obj):
        """Returns a short version of work description."""
        return obj.work_description[:40] + '...' if len(obj.work_description) > 40 else obj.work_description
    short_work_description.short_description = 'Work Description'
    
    def get_queryset(self, request):
        """Optimizes query with select_related."""
        return super().get_queryset(request).select_related('task__responsible_user')
