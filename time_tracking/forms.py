from django import forms
from .models import Task, TimeRecord
from django.utils import timezone


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks."""
    
    class Meta:
        model = Task
        fields = ['description', 'active']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Describe the task in detail...'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'description': 'Task Description',
            'active': 'Active Task',
        }
        help_texts = {
            'description': 'Describe in detail what needs to be done.',
            'active': 'Check if the task is active or completed.',
        }


class TimeRecordForm(forms.ModelForm):
    """Form for creating and editing time records."""
    
    class Meta:
        model = TimeRecord
        fields = ['task', 'record_date', 'worked_time', 'work_description']
        widgets = {
            'task': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select a task'
            }),
            'record_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Record date'
            }),
            'worked_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'placeholder': 'Worked time (HH:MM)'
            }),
            'work_description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe what was done during this period...'
            }),
        }
        labels = {
            'task': 'Task',
            'record_date': 'Record Date',
            'worked_time': 'Worked Time',
            'work_description': 'Work Description',
        }
        help_texts = {
            'task': 'Select the task you worked on.',
            'record_date': 'Date when the work was performed.',
            'worked_time': 'Duration of work (HH:MM format).',
            'work_description': 'Describe in detail what was done.',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter only user's tasks
            self.fields['task'].queryset = Task.objects.filter(
                responsible_user=user
            ).order_by('-creation_date')
    
    def clean_worked_time(self):
        """Custom validation for worked time."""
        time = self.cleaned_data.get('worked_time')
        if time and time.total_seconds() <= 0:
            raise forms.ValidationError(
                'Worked time must be greater than zero.'
            )
        return time
    
    def clean_record_date(self):
        """Custom validation for record date."""
        date = self.cleaned_data.get('record_date')
        if date and date > timezone.now().date():
            raise forms.ValidationError(
                'Record date cannot be in the future.'
            )
        return date 