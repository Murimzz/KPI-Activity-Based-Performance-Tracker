import os

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from accounts.serializers import UserBriefSerializer
from departments.models import Department
from departments.serializers import DepartmentSerializer
from tasks.models import Task, TaskCategory, TaskEvidence, TaskStatus


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = (
            'id',
            'name',
            'description',
            'default_expected_output',
            'default_expected_duration_minutes',
            'difficulty_level',
            'active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class TaskEvidenceSerializer(serializers.ModelSerializer):
    uploaded_by = UserBriefSerializer(read_only=True)

    class Meta:
        model = TaskEvidence
        fields = (
            'id',
            'task',
            'file',
            'file_name',
            'description',
            'uploaded_by',
            'uploaded_at',
        )
        read_only_fields = ('id', 'task', 'file_name', 'uploaded_by', 'uploaded_at')

    def validate_file(self, value):
        name = getattr(value, 'name', '') or ''
        ext = os.path.splitext(name)[1].lower()
        if ext not in settings.ALLOWED_EVIDENCE_EXTENSIONS:
            raise serializers.ValidationError(
                f'File type not allowed. Allowed: {", ".join(settings.ALLOWED_EVIDENCE_EXTENSIONS)}'
            )
        max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
        if value.size > max_size:
            raise serializers.ValidationError(
                f'File too large. Maximum size is {max_size // (1024 * 1024)} MB.'
            )
        return value


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserBriefSerializer(read_only=True)
    assigned_by = UserBriefSerializer(read_only=True)
    supervisor = UserBriefSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    category = TaskCategorySerializer(read_only=True)
    evidence = TaskEvidenceSerializer(many=True, read_only=True)

    assigned_to_id = serializers.PrimaryKeyRelatedField(
        source='assigned_to',
        queryset=Task._meta.get_field('assigned_to').related_model.objects.all(),
        write_only=True,
    )
    assigned_by_id = serializers.PrimaryKeyRelatedField(
        source='assigned_by',
        queryset=Task._meta.get_field('assigned_by').related_model.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    supervisor_id = serializers.PrimaryKeyRelatedField(
        source='supervisor',
        queryset=Task._meta.get_field('supervisor').related_model.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    department_id = serializers.PrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=TaskCategory.objects.filter(active=True),
        write_only=True,
    )

    class Meta:
        model = Task
        fields = (
            'id',
            'assigned_to',
            'assigned_to_id',
            'assigned_by',
            'assigned_by_id',
            'supervisor',
            'supervisor_id',
            'department',
            'department_id',
            'category',
            'category_id',
            'title',
            'description',
            'date_assigned',
            'due_date',
            'date_performed',
            'start_time',
            'end_time',
            'expected_output',
            'actual_output',
            'expected_duration_minutes',
            'actual_duration_minutes',
            'difficulty_level',
            'status',
            'challenges_encountered',
            'user_comments',
            'supervisor_comments',
            'supervisor_quality_rating',
            'supervisor_accuracy_rating',
            'supervisor_timeliness_rating',
            'submitted_at',
            'reviewed_at',
            'approved_at',
            'created_at',
            'updated_at',
            'evidence',
        )
        read_only_fields = (
            'id',
            'status',
            'supervisor_comments',
            'supervisor_quality_rating',
            'supervisor_accuracy_rating',
            'supervisor_timeliness_rating',
            'submitted_at',
            'reviewed_at',
            'approved_at',
            'created_at',
            'updated_at',
            'evidence',
        )

    def validate(self, attrs):
        date_assigned = attrs.get(
            'date_assigned',
            getattr(self.instance, 'date_assigned', None),
        )
        due_date = attrs.get('due_date', getattr(self.instance, 'due_date', None))
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        expected_output = attrs.get(
            'expected_output',
            getattr(self.instance, 'expected_output', None),
        )
        actual_output = attrs.get(
            'actual_output',
            getattr(self.instance, 'actual_output', None),
        )

        if due_date and date_assigned and due_date < date_assigned:
            raise serializers.ValidationError(
                {'due_date': 'Due date cannot be before the assigned date.'}
            )
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {'end_time': 'End time must be after start time.'}
            )
        if expected_output is not None and expected_output < 0:
            raise serializers.ValidationError(
                {'expected_output': 'Expected output cannot be negative.'}
            )
        if actual_output is not None and actual_output < 0:
            raise serializers.ValidationError(
                {'actual_output': 'Actual output cannot be negative.'}
            )
        return attrs


class TaskReviewSerializer(serializers.Serializer):
    supervisor_comments = serializers.CharField(required=False, allow_blank=True)
    supervisor_quality_rating = serializers.IntegerField(min_value=1, max_value=5)
    supervisor_accuracy_rating = serializers.IntegerField(min_value=1, max_value=5)
    supervisor_timeliness_rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        allow_null=True,
    )


class TaskRejectSerializer(serializers.Serializer):
    supervisor_comments = serializers.CharField(required=True, allow_blank=False)
    supervisor_quality_rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        allow_null=True,
    )
    supervisor_accuracy_rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        allow_null=True,
    )
    supervisor_timeliness_rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        allow_null=True,
    )
