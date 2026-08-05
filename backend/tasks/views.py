from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import UserRole
from accounts.permissions import IsAdminOrReadOnly, IsOwnerSupervisorOrAdmin
from audit.services import log_action
from performance.services import calculate_timeliness_score_for_task
from tasks.models import Task, TaskCategory, TaskStatus
from tasks.serializers import (
    TaskCategorySerializer,
    TaskEvidenceSerializer,
    TaskRejectSerializer,
    TaskReviewSerializer,
    TaskSerializer,
)


class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')
    user = filters.NumberFilter(field_name='assigned_to_id')
    supervisor = filters.NumberFilter(field_name='supervisor_id')
    department = filters.NumberFilter(field_name='department_id')
    category = filters.NumberFilter(field_name='category_id')
    difficulty = filters.CharFilter(field_name='difficulty_level')
    date_from = filters.DateFilter(field_name='date_assigned', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date_assigned', lookup_expr='lte')

    class Meta:
        model = Task
        fields = (
            'status',
            'user',
            'supervisor',
            'department',
            'category',
            'difficulty',
            'date_from',
            'date_to',
        )


class TaskCategoryViewSet(viewsets.ModelViewSet):
    queryset = TaskCategory.objects.all()
    serializer_class = TaskCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ('active', 'difficulty_level')
    search_fields = ('name', 'description')
    ordering = ('name',)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerSupervisorOrAdmin]
    filterset_class = TaskFilter
    search_fields = ('title', 'description', 'assigned_to__email')
    ordering_fields = ('date_assigned', 'due_date', 'created_at', 'status')
    ordering = ('-created_at',)
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related(
            'assigned_to',
            'assigned_by',
            'supervisor',
            'department',
            'category',
        ).prefetch_related('evidence')

        if user.role == UserRole.ADMIN or user.is_superuser:
            return qs
        if user.role == UserRole.SUPERVISOR:
            return qs.filter(Q(supervisor=user) | Q(assigned_to=user))
        return qs.filter(assigned_to=user)

    def perform_create(self, serializer):
        user = self.request.user
        extras = {}
        if 'assigned_by' not in serializer.validated_data:
            extras['assigned_by'] = user
        if serializer.validated_data.get('supervisor') is None:
            assigned_to = serializer.validated_data.get('assigned_to')
            if user.role == UserRole.SUPERVISOR:
                extras['supervisor'] = user
            elif assigned_to and assigned_to.supervisor_id:
                extras['supervisor'] = assigned_to.supervisor
        if serializer.validated_data.get('department') is None:
            assigned_to = serializer.validated_data.get('assigned_to', user)
            if getattr(assigned_to, 'department_id', None):
                extras['department'] = assigned_to.department

        task = serializer.save(status=TaskStatus.DRAFT, **extras)
        log_action(
            action='CREATE',
            model_name='Task',
            object_id=task.id,
            description=f'Task created: {task.title}',
            user=user,
        )

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        if user.role != UserRole.ADMIN and not user.is_superuser:
            if task.assigned_to_id != user.id:
                return Response(
                    {'detail': 'Only the assignee (or admin) can edit this task.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if task.status not in (TaskStatus.DRAFT, TaskStatus.REJECTED):
                return Response(
                    {'detail': 'Only draft or rejected tasks can be updated.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        kwargs['partial'] = kwargs.get('partial', False)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role != UserRole.ADMIN and not user.is_superuser:
            if instance.assigned_to_id != user.id or instance.status != TaskStatus.DRAFT:
                raise PermissionError(
                    'Only draft tasks can be deleted by the assignee.'
                )
        log_action(
            action='DELETE',
            model_name='Task',
            object_id=instance.id,
            description=f'Task deleted: {instance.title}',
            user=user,
        )
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'], url_path='my-tasks')
    def my_tasks(self, request):
        qs = self.filter_queryset(self.get_queryset().filter(assigned_to=request.user))
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='pending-review')
    def pending_review(self, request):
        user = request.user
        if (
            user.role not in (UserRole.SUPERVISOR, UserRole.ADMIN)
            and not user.is_superuser
        ):
            return Response(
                {'detail': 'Only supervisors and admins can view pending reviews.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = self.get_queryset().filter(status=TaskStatus.PENDING)
        if user.role == UserRole.SUPERVISOR:
            qs = qs.filter(supervisor=user)
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        task = self.get_object()
        if task.assigned_to_id != request.user.id and not (
            request.user.role == UserRole.ADMIN or request.user.is_superuser
        ):
            return Response(
                {'detail': 'Only the assignee can submit this task.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if task.status not in (TaskStatus.DRAFT, TaskStatus.REJECTED):
            return Response(
                {'detail': 'Only draft or rejected tasks can be submitted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.status = TaskStatus.PENDING
        task.submitted_at = timezone.now()
        task.save(update_fields=['status', 'submitted_at', 'updated_at'])
        log_action(
            action='SUBMIT',
            model_name='Task',
            object_id=task.id,
            description=f'Task submitted: {task.title}',
            user=request.user,
        )
        return Response(TaskSerializer(task, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        task = self.get_object()
        user = request.user

        if task.assigned_to_id == user.id:
            return Response(
                {'detail': 'Users cannot approve their own tasks.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if (
            user.role not in (UserRole.SUPERVISOR, UserRole.ADMIN)
            and not user.is_superuser
        ):
            return Response(
                {'detail': 'Only supervisors or admins can approve tasks.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if user.role == UserRole.SUPERVISOR and task.supervisor_id not in (
            None,
            user.id,
        ):
            return Response(
                {'detail': 'You are not the supervisor for this task.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if task.status != TaskStatus.PENDING:
            return Response(
                {'detail': 'Only pending tasks can be approved.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TaskReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            task.status = TaskStatus.APPROVED
            task.supervisor_comments = data.get('supervisor_comments', '')
            task.supervisor_quality_rating = data['supervisor_quality_rating']
            task.supervisor_accuracy_rating = data['supervisor_accuracy_rating']
            if data.get('supervisor_timeliness_rating') is not None:
                task.supervisor_timeliness_rating = data[
                    'supervisor_timeliness_rating'
                ]
            task.reviewed_at = timezone.now()
            task.approved_at = timezone.now()
            if task.supervisor_id is None:
                task.supervisor = user
            task.save()
            log_action(
                action='APPROVE',
                model_name='Task',
                object_id=task.id,
                description=f'Task approved: {task.title}',
                user=user,
            )

        payload = TaskSerializer(task, context={'request': request}).data
        payload['preliminary_timeliness_score'] = str(
            calculate_timeliness_score_for_task(task)
        )
        return Response(payload)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        task = self.get_object()
        user = request.user

        if task.assigned_to_id == user.id:
            return Response(
                {'detail': 'Users cannot reject their own tasks.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if (
            user.role not in (UserRole.SUPERVISOR, UserRole.ADMIN)
            and not user.is_superuser
        ):
            return Response(
                {'detail': 'Only supervisors or admins can reject tasks.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if task.status != TaskStatus.PENDING:
            return Response(
                {'detail': 'Only pending tasks can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TaskRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            task.status = TaskStatus.REJECTED
            task.supervisor_comments = data['supervisor_comments']
            for field in (
                'supervisor_quality_rating',
                'supervisor_accuracy_rating',
                'supervisor_timeliness_rating',
            ):
                if data.get(field) is not None:
                    setattr(task, field, data[field])
            task.reviewed_at = timezone.now()
            if task.supervisor_id is None:
                task.supervisor = user
            task.save()
            log_action(
                action='REJECT',
                model_name='Task',
                object_id=task.id,
                description=f'Task rejected: {task.title}',
                user=user,
            )

        return Response(TaskSerializer(task, context={'request': request}).data)

    @action(
        detail=True,
        methods=['post'],
        url_path='evidence',
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_evidence(self, request, pk=None):
        task = self.get_object()
        user = request.user
        if (
            task.assigned_to_id != user.id
            and user.role not in (UserRole.ADMIN, UserRole.SUPERVISOR)
            and not user.is_superuser
        ):
            return Response(
                {'detail': 'You cannot upload evidence for this task.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if task.status not in (
            TaskStatus.DRAFT,
            TaskStatus.REJECTED,
            TaskStatus.PENDING,
        ):
            return Response(
                {'detail': 'Evidence cannot be added in the current status.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TaskEvidenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        evidence = serializer.save(task=task, uploaded_by=user)
        log_action(
            action='UPLOAD_EVIDENCE',
            model_name='TaskEvidence',
            object_id=evidence.id,
            description=f'Evidence uploaded for task {task.id}',
            user=user,
        )
        return Response(
            TaskEvidenceSerializer(evidence, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
