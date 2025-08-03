from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.urls import reverse


class Task(models.Model):
    """
    Model for representing a task in the time tracking system.
    """
    responsible_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Responsible User",
        related_name="tasks"
    )
    creation_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Creation Date"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Describe the task in detail"
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Active Task",
        help_text="Indicates if the task is active or completed"
    )
    
    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-creation_date']
        indexes = [
            models.Index(fields=['responsible_user', '-creation_date']),
            models.Index(fields=['active', '-creation_date']),
        ]
    
    def __str__(self):
        return f"{self.description[:50]} - {self.responsible_user.username}"
    
    def get_absolute_url(self):
        return reverse('task-detail', kwargs={'pk': self.pk})
    
    @property
    def total_worked_time(self):
        """Returns total time worked on this task."""
        return self.time_records.aggregate(
            total=models.Sum('worked_time')
        )['total'] or timezone.timedelta(0)
    
    @property
    def total_hours(self):
        """Returns total hours worked formatted."""
        total = self.total_worked_time
        hours = total.total_seconds() / 3600
        return f"{hours:.2f} hours"


class TimeRecord(models.Model):
    """
    Model for representing a time record worked on a task.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name="Task",
        related_name="time_records"
    )
    record_date = models.DateField(
        verbose_name="Record Date",
        default=timezone.now
    )
    worked_time = models.DurationField(
        verbose_name="Worked Time",
        validators=[MinValueValidator(timezone.timedelta(minutes=1))]
    )
    work_description = models.TextField(
        verbose_name="Work Description",
        help_text="Describe what was done during this period"
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Record Creation Date"
    )
    
    class Meta:
        verbose_name = "Time Record"
        verbose_name_plural = "Time Records"
        ordering = ['-record_date', '-creation_date']
        indexes = [
            models.Index(fields=['task', '-record_date']),
            models.Index(fields=['record_date', '-creation_date']),
        ]
    
    def __str__(self):
        return f"{self.task.description[:30]} - {self.record_date} ({self.worked_time})"
    
    def get_absolute_url(self):
        return reverse('record-detail', kwargs={'pk': self.pk})
    
    @property
    def worked_hours(self):
        """Returns worked hours formatted."""
        total_seconds = self.worked_time.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"
    
    def clean(self):
        """Custom model validation."""
        from django.core.exceptions import ValidationError
        
        if self.worked_time and self.worked_time.total_seconds() <= 0:
            raise ValidationError({
                'worked_time': 'Worked time must be greater than zero.'
            })
        
        if self.record_date and self.record_date > timezone.now().date():
            raise ValidationError({
                'record_date': 'Record date cannot be in the future.'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
