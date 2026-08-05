from decimal import Decimal

from django.test import TestCase

from performance.services import (
    calculate_completion_rate,
    calculate_output_achievement,
    calculate_time_efficiency,
    calculate_overall_activity_score,
    classify_performance,
)
from tasks.models import Task, TaskStatus


class KPIFormulaTests(TestCase):
    def test_completion_rate_zero_when_no_tasks(self):
        self.assertEqual(calculate_completion_rate([]), Decimal('0.00'))

    def test_output_achievement_caps_at_120(self):
        task = Task(
            status=TaskStatus.APPROVED,
            expected_output=Decimal('10'),
            actual_output=Decimal('20'),
        )
        self.assertEqual(calculate_output_achievement([task]), Decimal('120.00'))

    def test_time_efficiency_excludes_zero_actual(self):
        task = Task(
            status=TaskStatus.APPROVED,
            expected_duration_minutes=60,
            actual_duration_minutes=0,
        )
        self.assertEqual(calculate_time_efficiency([task]), Decimal('0.00'))

    def test_overall_score_capped_at_100(self):
        metrics = {
            'completion_rate': Decimal('120'),
            'output_achievement': Decimal('120'),
            'time_efficiency': Decimal('120'),
            'quality_score': Decimal('100'),
            'accuracy_score': Decimal('100'),
            'attendance_score': Decimal('100'),
        }
        self.assertEqual(calculate_overall_activity_score(metrics), Decimal('100.00'))

    def test_classification_bands(self):
        self.assertEqual(classify_performance(95), 'Excellent')
        self.assertEqual(classify_performance(85), 'Very Good')
        self.assertEqual(classify_performance(75), 'Good')
        self.assertEqual(classify_performance(65), 'Satisfactory')
        self.assertEqual(classify_performance(55), 'Needs Improvement')
        self.assertEqual(classify_performance(40), 'Unsatisfactory')
