from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Task, TimeRecord
from .forms import TaskForm, TimeRecordForm


@login_required
def dashboard(request):
    """Main dashboard page."""
    user = request.user
    
    # Statistics
    tasks = Task.objects.filter(responsible_user=user)
    total_tasks = tasks.count()
    active_tasks = tasks.filter(active=True).count()
    
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
    
    # Recent data
    recent_tasks = tasks.order_by('-creation_date')[:5]
    recent_records = records.order_by('-creation_date')[:10]
    
    context = {
        'total_tasks': total_tasks,
        'active_tasks': active_tasks,
        'total_hours': total_hours.total_seconds() / 3600,
        'week_hours': week_hours.total_seconds() / 3600,
        'recent_tasks': recent_tasks,
        'recent_records': recent_records,
    }
    
    return render(request, 'time_tracking/dashboard.html', context)


@login_required
def task_list(request):
    """Lists all user tasks."""
    tasks = Task.objects.filter(responsible_user=request.user)
    
    # Filters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        tasks = tasks.filter(
            Q(description__icontains=search) |
            Q(responsible_user__username__icontains=search)
        )
    
    if status_filter == 'active':
        tasks = tasks.filter(active=True)
    elif status_filter == 'inactive':
        tasks = tasks.filter(active=False)
    
    tasks = tasks.order_by('-creation_date')
    
    context = {
        'tasks': tasks,
        'search': search,
        'status_filter': status_filter,
    }
    
    return render(request, 'time_tracking/task_list.html', context)


@login_required
def new_task(request):
    """Creates a new task."""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.responsible_user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'title': 'New Task'
    }
    
    return render(request, 'time_tracking/task_form.html', context)


@login_required
def edit_task(request, pk):
    """Edits an existing task."""
    task = get_object_or_404(Task, pk=pk, responsible_user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': 'Edit Task'
    }
    
    return render(request, 'time_tracking/task_form.html', context)


@login_required
def task_detail(request, pk):
    """Shows task details."""
    task = get_object_or_404(Task, pk=pk, responsible_user=request.user)
    records = task.time_records.order_by('-record_date')
    
    context = {
        'task': task,
        'records': records,
    }
    
    return render(request, 'time_tracking/task_detail.html', context)


@login_required
def record_list(request):
    """Lists all user time records."""
    records = TimeRecord.objects.filter(task__responsible_user=request.user)
    
    # Filters
    search = request.GET.get('search', '')
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    period = request.GET.get('period', '')
    
    if search:
        records = records.filter(
            Q(work_description__icontains=search) |
            Q(task__description__icontains=search)
        )
    
    if date_start:
        records = records.filter(record_date__gte=date_start)
    
    if date_end:
        records = records.filter(record_date__lte=date_end)
    
    if period:
        today = timezone.now().date()
        if period == 'today':
            records = records.filter(record_date=today)
        elif period == 'this_week':
            week_start = today - timedelta(days=today.weekday())
            records = records.filter(record_date__gte=week_start)
        elif period == 'this_month':
            month_start = today.replace(day=1)
            records = records.filter(record_date__gte=month_start)
    
    records = records.order_by('-record_date')
    
    context = {
        'records': records,
        'search': search,
        'date_start': date_start,
        'date_end': date_end,
        'period': period,
    }
    
    return render(request, 'time_tracking/record_list.html', context)


@login_required
def new_record(request):
    """Creates a new time record."""
    if request.method == 'POST':
        form = TimeRecordForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Time record created successfully!')
            return redirect('record_list')
    else:
        form = TimeRecordForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'New Time Record'
    }
    
    return render(request, 'time_tracking/record_form.html', context)


@login_required
def edit_record(request, pk):
    """Edits an existing time record."""
    record = get_object_or_404(
        TimeRecord, 
        pk=pk, 
        task__responsible_user=request.user
    )
    
    if request.method == 'POST':
        form = TimeRecordForm(request.POST, instance=record, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Time record updated successfully!')
            return redirect('record_list')
    else:
        form = TimeRecordForm(instance=record, user=request.user)
    
    context = {
        'form': form,
        'record': record,
        'title': 'Edit Time Record'
    }
    
    return render(request, 'time_tracking/record_form.html', context) 