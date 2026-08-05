from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from decimal import Decimal


class PeriodType(models.TextChoices):
    WEEKLY = 'WEEKLY', 'Weekly'
    MONTHLY = 'MONTHLY', 'Monthly'
    QUARTERLY = 'QUARTERLY', 'Quarterly'


class KPIWeight(models.Model):
    """
    Configurable weight for a Contribution Score metric.

    Active weights must sum to 100%.
    """

    name = models.CharField(max_length=100)
    metric_key = models.CharField(
        max_length=50,
        unique=True,
        help_text=(
            'Stable key used by calculation services, e.g. completion_rate, '
            'output_achievement, time_efficiency, quality_score, '
            'accuracy_score, attendance_score.'
        ),
    )
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['metric_key']
        verbose_name = 'KPI weight'
        verbose_name_plural = 'KPI weights'
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['metric_key']),
        ]

    def __str__(self):
        return f'{self.name} ({self.weight_percentage}%)'

    def clean(self):
        if self.weight_percentage is not None and self.weight_percentage < 0:
            raise ValidationError(
                {'weight_percentage': 'Weight percentage cannot be negative.'}
            )
        if self.weight_percentage is not None and self.weight_percentage > 100:
            raise ValidationError(
                {'weight_percentage': 'Weight percentage cannot exceed 100.'}
            )

        qs = KPIWeight.objects.filter(active=True)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        others_total = qs.aggregate(total=Sum('weight_percentage'))['total'] or Decimal('0')

        if self.active:
            this_weight = self.weight_percentage if self.weight_percentage is not None else Decimal('0')
            total = others_total + this_weight
        else:
            # Saving inactive / deactivating: remaining active weights must still total 100 if any.
            total = others_total
            if not qs.exists():
                return

        if total != Decimal('100') and total != Decimal('100.00'):
            raise ValidationError(
                {
                    'weight_percentage': (
                        f'Active KPI weights must add up to 100%. '
                        f'Current total would be {total}%. '
                        f'Prefer: python manage.py seed_default_kpi_weights'
                    )
                }
            )

    def save(self, *args, skip_weight_validation=False, **kwargs):
        if skip_weight_validation:
            # Still validate non-sum field rules lightly.
            if self.weight_percentage is not None and self.weight_percentage < 0:
                raise ValidationError(
                    {'weight_percentage': 'Weight percentage cannot be negative.'}
                )
            models.Model.save(self, *args, **kwargs)
            return
        self.full_clean()
        super().save(*args, **kwargs)


class PerformanceSnapshot(models.Model):
    """
    Stored Activity Performance / Contribution Score for a user and period.

    This is not an official government performance appraisal.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='performance_snapshots',
    )
    period_type = models.CharField(
        max_length=20,
        choices=PeriodType.choices,
        db_index=True,
    )
    period_start = models.DateField()
    period_end = models.DateField()
    completion_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    output_achievement = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    time_efficiency = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    quality_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    accuracy_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    attendance_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overall_activity_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text='Overall Contribution Score (capped at 100).',
    )
    approved_tasks = models.PositiveIntegerField(default=0)
    pending_tasks = models.PositiveIntegerField(default=0)
    rejected_tasks = models.PositiveIntegerField(default=0)
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_end', '-created_at']
        verbose_name = 'Performance snapshot'
        verbose_name_plural = 'Performance snapshots'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'period_type', 'period_start', 'period_end'],
                name='unique_performance_snapshot_period',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'period_type']),
            models.Index(fields=['period_start', 'period_end']),
        ]

    def __str__(self):
        return (
            f'{self.user} {self.period_type} '
            f'{self.period_start}–{self.period_end}: '
            f'{self.overall_activity_score}'
        )

    def clean(self):
        if self.period_end and self.period_start and self.period_end < self.period_start:
            raise ValidationError(
                {'period_end': 'Period end cannot be before period start.'}
            )
