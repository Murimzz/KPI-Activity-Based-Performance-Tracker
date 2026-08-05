from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class DifficultyLevel(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    COMPLEX = 'COMPLEX', 'Complex'


class TaskStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class TaskCategory(models.Model):
    """
    Category used when creating tasks.

    Supplies default expected output and duration for new tasks.
    """

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    default_expected_output = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        help_text='Default expected output quantity for tasks in this category.',
    )
    default_expected_duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text='Default expected duration in minutes.',
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.MEDIUM,
        db_index=True,
    )
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Task category'
        verbose_name_plural = 'Task categories'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['active']),
            models.Index(fields=['difficulty_level']),
        ]

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Assigned work item used for Activity Performance / Contribution Score.

    Only APPROVED tasks should contribute to final performance calculations
    (KPI services are added in a later phase).
    """

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned_by_me',
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_tasks',
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.PROTECT,
        related_name='tasks',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_assigned = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    date_performed = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    expected_output = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    actual_output = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    expected_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    actual_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.MEDIUM,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.DRAFT,
        db_index=True,
    )
    challenges_encountered = models.TextField(blank=True)
    user_comments = models.TextField(blank=True)
    supervisor_comments = models.TextField(blank=True)
    supervisor_quality_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Quality rating from 1 to 5.',
    )
    supervisor_accuracy_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Accuracy rating from 1 to 5.',
    )
    supervisor_timeliness_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Timeliness rating from 1 to 5 (optional override).',
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['date_assigned']),
            models.Index(fields=['due_date']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['supervisor', 'status']),
            models.Index(fields=['department', 'status']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return f'{self.title} ({self.status})'

    def clean(self):
        errors = {}

        if self.due_date and self.date_assigned and self.due_date < self.date_assigned:
            errors['due_date'] = 'Due date cannot be before the assigned date.'

        if self.start_time and self.end_time and self.end_time <= self.start_time:
            # Allow overnight only when date_performed spans; for Phase 3 require end > start.
            errors['end_time'] = 'End time must be after start time.'

        if self.expected_output is not None and self.expected_output < 0:
            errors['expected_output'] = 'Expected output cannot be negative.'

        if self.actual_output is not None and self.actual_output < 0:
            errors['actual_output'] = 'Actual output cannot be negative.'

        for field_name in (
            'supervisor_quality_rating',
            'supervisor_accuracy_rating',
            'supervisor_timeliness_rating',
        ):
            value = getattr(self, field_name)
            if value is not None and (value < 1 or value > 5):
                errors[field_name] = 'Rating must be between 1 and 5.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if (
            self.actual_duration_minutes is None
            and self.start_time
            and self.end_time
            and self.end_time > self.start_time
        ):
            start_dt = datetime.combine(datetime.min, self.start_time)
            end_dt = datetime.combine(datetime.min, self.end_time)
            self.actual_duration_minutes = int((end_dt - start_dt).total_seconds() // 60)

        if self.category_id:
            if self.expected_output is None:
                self.expected_output = self.category.default_expected_output
            if self.expected_duration_minutes is None:
                self.expected_duration_minutes = (
                    self.category.default_expected_duration_minutes
                )
            if not self.difficulty_level:
                self.difficulty_level = self.category.difficulty_level

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_editable_by_assignee(self):
        """Assignees may update draft or rejected tasks only."""
        return self.status in (TaskStatus.DRAFT, TaskStatus.REJECTED)

    @property
    def contributes_to_performance(self):
        """Only approved tasks feed final Contribution Score calculations."""
        return self.status == TaskStatus.APPROVED


def task_evidence_upload_to(instance, filename):
    return f'task_evidence/{instance.task_id}/{filename}'


class TaskEvidence(models.Model):
    """Supporting file attached to a task (PDF, images, DOCX, XLSX)."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='evidence',
    )
    file = models.FileField(upload_to=task_evidence_upload_to)
    file_name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=500, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_evidence',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Task evidence'
        verbose_name_plural = 'Task evidence'
        indexes = [
            models.Index(fields=['task', 'uploaded_at']),
        ]

    def __str__(self):
        return self.file_name or self.file.name

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = getattr(self.file, 'name', '') or ''
            # Keep only the basename if a path was provided.
            self.file_name = self.file_name.replace('\\', '/').split('/')[-1]
        super().save(*args, **kwargs)
