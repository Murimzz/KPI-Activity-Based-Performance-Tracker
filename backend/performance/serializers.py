from rest_framework import serializers

from performance.models import KPIWeight, PerformanceSnapshot
from accounts.serializers import UserBriefSerializer


class KPIWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIWeight
        fields = (
            'id',
            'name',
            'metric_key',
            'weight_percentage',
            'active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PerformanceSnapshotSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = PerformanceSnapshot
        fields = (
            'id',
            'user',
            'period_type',
            'period_start',
            'period_end',
            'completion_rate',
            'output_achievement',
            'time_efficiency',
            'quality_score',
            'accuracy_score',
            'attendance_score',
            'overall_activity_score',
            'approved_tasks',
            'pending_tasks',
            'rejected_tasks',
            'total_hours',
            'created_at',
        )
        read_only_fields = fields
