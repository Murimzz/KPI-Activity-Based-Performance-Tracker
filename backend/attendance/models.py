from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', 'Present'
    ABSENT = 'ABSENT', 'Absent'
    LATE = 'LATE', 'Late'
    OFFICIAL_DUTY = 'OFFICIAL_DUTY', 'Official duty'
    LEAVE = 'LEAVE', 'Leave'


class AttendanceRecord(models.Model):
    """Daily attendance used for the Attendance Score component of Contribution Score."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    date = models.DateField(db_index=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
        db_index=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'user_id']
        verbose_name = 'Attendance record'
        verbose_name_plural = 'Attendance records'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date'],
                name='unique_attendance_per_user_date',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.user} — {self.date} ({self.status})'

    def clean(self):
        if (
            self.check_in_time
            and self.check_out_time
            and self.check_out_time <= self.check_in_time
        ):
            raise ValidationError(
                {'check_out_time': 'Check-out time must be after check-in time.'}
            )
