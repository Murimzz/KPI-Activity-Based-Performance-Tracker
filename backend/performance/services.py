"""
KPI / Contribution Score calculation services.

Business logic lives here — not in serializers or views.
Scores are Activity Performance / Contribution Scores, not official appraisals.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from django.db.models import QuerySet
from django.utils import timezone

from attendance.models import AttendanceRecord, AttendanceStatus
from performance.models import KPIWeight, PerformanceSnapshot
from tasks.models import Task, TaskStatus

TWO_PLACES = Decimal('0.01')
HUNDRED = Decimal('100')
CAP_120 = Decimal('120')

DEFAULT_KPI_WEIGHTS = (
    ('Completion Rate', 'completion_rate', Decimal('25.00')),
    ('Output Achievement', 'output_achievement', Decimal('25.00')),
    ('Time Efficiency', 'time_efficiency', Decimal('15.00')),
    ('Quality Score', 'quality_score', Decimal('20.00')),
    ('Accuracy Score', 'accuracy_score', Decimal('10.00')),
    ('Attendance Score', 'attendance_score', Decimal('5.00')),
)


def _as_decimal(value) -> Decimal:
    if value is None:
        return Decimal('0')
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _round2(value: Decimal) -> Decimal:
    return _as_decimal(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _cap(value: Decimal, maximum: Decimal = CAP_120) -> Decimal:
    return min(_as_decimal(value), maximum)


def classify_performance(overall_score) -> str:
    """Map overall Contribution Score to a performance classification label."""
    score = _as_decimal(overall_score)
    if score >= Decimal('90'):
        return 'Excellent'
    if score >= Decimal('80'):
        return 'Very Good'
    if score >= Decimal('70'):
        return 'Good'
    if score >= Decimal('60'):
        return 'Satisfactory'
    if score >= Decimal('50'):
        return 'Needs Improvement'
    return 'Unsatisfactory'


def get_active_kpi_weights() -> dict[str, Decimal]:
    """
    Return metric_key -> weight fraction (0–1) for active KPI weights.

    Falls back to built-in defaults if none are configured.
    """
    rows = list(
        KPIWeight.objects.filter(active=True).values('metric_key', 'weight_percentage')
    )
    if not rows:
        return {key: pct / HUNDRED for _name, key, pct in DEFAULT_KPI_WEIGHTS}

    return {
        r['metric_key']: _as_decimal(r['weight_percentage']) / HUNDRED for r in rows
    }


def tasks_in_period(
    user,
    period_start: date,
    period_end: date,
) -> QuerySet[Task]:
    """Tasks assigned to the user whose date_assigned falls in the period."""
    return Task.objects.filter(
        assigned_to=user,
        date_assigned__gte=period_start,
        date_assigned__lte=period_end,
    )


def calculate_completion_rate(tasks: Iterable[Task] | QuerySet) -> Decimal:
    """approved tasks / total assigned tasks * 100."""
    task_list = list(tasks)
    total = len(task_list)
    if total == 0:
        return Decimal('0.00')
    approved = sum(1 for t in task_list if t.status == TaskStatus.APPROVED)
    return _round2(Decimal(approved) / Decimal(total) * HUNDRED)


def calculate_output_achievement(approved_tasks: Iterable[Task]) -> Decimal:
    """Average of actual/expected*100 for approved tasks; each capped at 120%."""
    scores = []
    for task in approved_tasks:
        expected = task.expected_output
        if expected is None or expected == 0:
            continue
        actual = task.actual_output
        if actual is None:
            continue
        scores.append(_cap(_as_decimal(actual) / _as_decimal(expected) * HUNDRED))
    if not scores:
        return Decimal('0.00')
    return _round2(sum(scores) / Decimal(len(scores)))


def calculate_time_efficiency(approved_tasks: Iterable[Task]) -> Decimal:
    """Average of expected/actual*100 for approved tasks; each capped at 120%."""
    scores = []
    for task in approved_tasks:
        actual = task.actual_duration_minutes
        if actual is None or actual == 0:
            continue
        expected = task.expected_duration_minutes
        if expected is None:
            continue
        scores.append(_cap(_as_decimal(expected) / _as_decimal(actual) * HUNDRED))
    if not scores:
        return Decimal('0.00')
    return _round2(sum(scores) / Decimal(len(scores)))


def calculate_quality_score(approved_tasks: Iterable[Task]) -> Decimal:
    """Average of supervisor_quality_rating / 5 * 100."""
    ratings = [
        t.supervisor_quality_rating
        for t in approved_tasks
        if t.supervisor_quality_rating is not None
    ]
    if not ratings:
        return Decimal('0.00')
    avg = sum(Decimal(r) for r in ratings) / Decimal(len(ratings))
    return _round2(avg / Decimal('5') * HUNDRED)


def calculate_accuracy_score(approved_tasks: Iterable[Task]) -> Decimal:
    """Average of supervisor_accuracy_rating / 5 * 100."""
    ratings = [
        t.supervisor_accuracy_rating
        for t in approved_tasks
        if t.supervisor_accuracy_rating is not None
    ]
    if not ratings:
        return Decimal('0.00')
    avg = sum(Decimal(r) for r in ratings) / Decimal(len(ratings))
    return _round2(avg / Decimal('5') * HUNDRED)


def calculate_timeliness_score_for_task(task: Task) -> Decimal:
    """
    Timeliness for a single task.

    Prefer supervisor_timeliness_rating (1–5 → %) when set; otherwise
    derive from due date vs completion/submission date.
    """
    if task.supervisor_timeliness_rating is not None:
        return _round2(
            Decimal(task.supervisor_timeliness_rating) / Decimal('5') * HUNDRED
        )

    if task.status in (TaskStatus.DRAFT, TaskStatus.CANCELLED):
        return Decimal('0.00')

    if not task.due_date:
        return HUNDRED

    completed_on = None
    if task.approved_at:
        completed_on = timezone.localdate(task.approved_at)
    elif task.submitted_at:
        completed_on = timezone.localdate(task.submitted_at)
    elif task.date_performed:
        completed_on = task.date_performed

    if completed_on is None:
        return Decimal('0.00')

    delta_days = (completed_on - task.due_date).days
    if delta_days <= 0:
        return HUNDRED
    if delta_days == 1:
        return Decimal('90.00')
    if delta_days == 2:
        return Decimal('80.00')
    return Decimal('70.00')


def calculate_attendance_score(
    user,
    period_start: date,
    period_end: date,
    expected_working_days: int | None = None,
) -> Decimal:
    """
    days_present / expected_working_days * 100.

    PRESENT and LATE count as present.
    OFFICIAL_DUTY and LEAVE are excluded from expected working days (not absences).
    """
    records = list(
        AttendanceRecord.objects.filter(
            user=user,
            date__gte=period_start,
            date__lte=period_end,
        )
    )

    excluded = {AttendanceStatus.OFFICIAL_DUTY, AttendanceStatus.LEAVE}
    present_statuses = {AttendanceStatus.PRESENT, AttendanceStatus.LATE}

    counted_records = [r for r in records if r.status not in excluded]
    days_present = sum(1 for r in counted_records if r.status in present_statuses)

    if expected_working_days is None:
        expected = 0
        current = period_start
        excluded_dates = {r.date for r in records if r.status in excluded}
        while current <= period_end:
            if current.weekday() < 5 and current not in excluded_dates:
                expected += 1
            current += timedelta(days=1)
        expected_working_days = expected

    if expected_working_days <= 0:
        return Decimal('0.00')

    return _round2(Decimal(days_present) / Decimal(expected_working_days) * HUNDRED)


def calculate_overall_activity_score(metrics: dict[str, Decimal]) -> Decimal:
    """Weighted overall Contribution Score, capped at 100."""
    weights = get_active_kpi_weights()
    overall = Decimal('0')
    for key, weight in weights.items():
        overall += _as_decimal(metrics.get(key, 0)) * weight
    return min(_round2(overall), HUNDRED)


def calculate_total_hours(approved_tasks: Iterable[Task]) -> Decimal:
    minutes = sum((t.actual_duration_minutes or 0) for t in approved_tasks)
    return _round2(Decimal(minutes) / Decimal('60'))


def build_user_performance_metrics(
    user,
    period_start: date,
    period_end: date,
) -> dict:
    """Compute all metrics for a user in a reporting period."""
    task_list = list(tasks_in_period(user, period_start, period_end))
    approved = [t for t in task_list if t.status == TaskStatus.APPROVED]
    pending = sum(1 for t in task_list if t.status == TaskStatus.PENDING)
    rejected = sum(1 for t in task_list if t.status == TaskStatus.REJECTED)

    metrics = {
        'completion_rate': calculate_completion_rate(task_list),
        'output_achievement': calculate_output_achievement(approved),
        'time_efficiency': calculate_time_efficiency(approved),
        'quality_score': calculate_quality_score(approved),
        'accuracy_score': calculate_accuracy_score(approved),
        'attendance_score': calculate_attendance_score(user, period_start, period_end),
    }
    overall = calculate_overall_activity_score(metrics)

    return {
        **metrics,
        'overall_activity_score': overall,
        'performance_classification': classify_performance(overall),
        'approved_tasks': len(approved),
        'pending_tasks': pending,
        'rejected_tasks': rejected,
        'total_assigned_tasks': len(task_list),
        'total_hours': calculate_total_hours(approved),
        'period_start': period_start,
        'period_end': period_end,
    }


def create_or_update_performance_snapshot(
    user,
    period_type: str,
    period_start: date,
    period_end: date,
) -> PerformanceSnapshot:
    """Persist a PerformanceSnapshot from live calculations."""
    data = build_user_performance_metrics(user, period_start, period_end)
    snapshot, _created = PerformanceSnapshot.objects.update_or_create(
        user=user,
        period_type=period_type,
        period_start=period_start,
        period_end=period_end,
        defaults={
            'completion_rate': data['completion_rate'],
            'output_achievement': data['output_achievement'],
            'time_efficiency': data['time_efficiency'],
            'quality_score': data['quality_score'],
            'accuracy_score': data['accuracy_score'],
            'attendance_score': data['attendance_score'],
            'overall_activity_score': data['overall_activity_score'],
            'approved_tasks': data['approved_tasks'],
            'pending_tasks': data['pending_tasks'],
            'rejected_tasks': data['rejected_tasks'],
            'total_hours': data['total_hours'],
        },
    )
    return snapshot
