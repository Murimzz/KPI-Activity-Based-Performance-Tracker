import csv
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from accounts.permissions import IsSupervisorOrAdmin
from performance.services import build_user_performance_metrics
from tasks.models import Task, TaskStatus

User = get_user_model()


def _parse_range(request, default_days=30):
    today = timezone.localdate()
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    if start and end:
        from datetime import date as date_cls

        return date_cls.fromisoformat(start), date_cls.fromisoformat(end)
    return today - timedelta(days=default_days), today


def _can_view_user(request, target):
    user = request.user
    if user.is_superuser or user.role == UserRole.ADMIN:
        return True
    if user.id == target.id:
        return True
    if user.role == UserRole.SUPERVISOR and target.supervisor_id == user.id:
        return True
    return False


class UserReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            target = User.objects.select_related('department', 'supervisor').get(
                pk=user_id
            )
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)
        if not _can_view_user(request, target):
            return Response({'detail': 'Not allowed.'}, status=403)

        start, end = _parse_range(request)
        metrics = build_user_performance_metrics(target, start, end)
        category_breakdown = (
            Task.objects.filter(
                assigned_to=target,
                date_assigned__gte=start,
                date_assigned__lte=end,
            )
            .values('category__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return Response(
            {
                'user': {
                    'id': target.id,
                    'full_name': target.get_full_name(),
                    'email': target.email,
                    'department': target.department.name if target.department else None,
                    'supervisor': (
                        target.supervisor.get_full_name()
                        if target.supervisor
                        else None
                    ),
                },
                'reporting_period': {'start': start, 'end': end},
                'metrics': metrics,
                'category_breakdown': list(category_breakdown),
                'disclaimer': (
                    'Overall Activity Score is a Contribution Score, '
                    'not an official government performance appraisal.'
                ),
            }
        )


class WeeklyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        end = timezone.localdate()
        start = end - timedelta(days=7)
        target_id = request.query_params.get('user_id', request.user.id)
        try:
            target = User.objects.get(pk=target_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)
        if not _can_view_user(request, target):
            return Response({'detail': 'Not allowed.'}, status=403)
        metrics = build_user_performance_metrics(target, start, end)
        return Response(
            {
                'period_type': 'WEEKLY',
                'period_start': start,
                'period_end': end,
                'user_id': target.id,
                'metrics': metrics,
            }
        )


class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        end = timezone.localdate()
        start = end.replace(day=1)
        target_id = request.query_params.get('user_id', request.user.id)
        try:
            target = User.objects.get(pk=target_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)
        if not _can_view_user(request, target):
            return Response({'detail': 'Not allowed.'}, status=403)
        metrics = build_user_performance_metrics(target, start, end)
        return Response(
            {
                'period_type': 'MONTHLY',
                'period_start': start,
                'period_end': end,
                'user_id': target.id,
                'metrics': metrics,
            }
        )


class CategoryBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_range(request)
        qs = Task.objects.filter(date_assigned__gte=start, date_assigned__lte=end)
        user = request.user
        if user.role == UserRole.SUPERVISOR:
            qs = qs.filter(supervisor=user)
        elif user.role not in (UserRole.ADMIN,) and not user.is_superuser:
            qs = qs.filter(assigned_to=user)
        data = (
            qs.values('category__id', 'category__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return Response({'period_start': start, 'period_end': end, 'breakdown': list(data)})


class StatusBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_range(request)
        qs = Task.objects.filter(date_assigned__gte=start, date_assigned__lte=end)
        user = request.user
        if user.role == UserRole.SUPERVISOR:
            qs = qs.filter(supervisor=user)
        elif user.role not in (UserRole.ADMIN,) and not user.is_superuser:
            qs = qs.filter(assigned_to=user)
        data = qs.values('status').annotate(count=Count('id')).order_by('status')
        return Response({'period_start': start, 'period_end': end, 'breakdown': list(data)})


class ExportCSVView(APIView):
    permission_classes = [IsSupervisorOrAdmin]

    def get(self, request):
        start, end = _parse_range(request)
        user = request.user
        if user.role == UserRole.ADMIN or user.is_superuser:
            members = User.objects.filter(
                role__in=(UserRole.INTERN, UserRole.STAFF, UserRole.SUPERVISOR)
            )
        else:
            members = User.objects.filter(supervisor=user)

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                'user_name',
                'email',
                'department',
                'supervisor',
                'period_start',
                'period_end',
                'assigned_tasks',
                'approved_tasks',
                'pending_tasks',
                'rejected_tasks',
                'total_hours',
                'completion_rate',
                'output_achievement',
                'time_efficiency',
                'quality_score',
                'accuracy_score',
                'attendance_score',
                'overall_activity_score',
                'performance_classification',
            ]
        )
        for member in members.select_related('department', 'supervisor'):
            m = build_user_performance_metrics(member, start, end)
            writer.writerow(
                [
                    member.get_full_name(),
                    member.email,
                    member.department.name if member.department else '',
                    member.supervisor.get_full_name() if member.supervisor else '',
                    start,
                    end,
                    m['total_assigned_tasks'],
                    m['approved_tasks'],
                    m['pending_tasks'],
                    m['rejected_tasks'],
                    m['total_hours'],
                    m['completion_rate'],
                    m['output_achievement'],
                    m['time_efficiency'],
                    m['quality_score'],
                    m['accuracy_score'],
                    m['attendance_score'],
                    m['overall_activity_score'],
                    m['performance_classification'],
                ]
            )

        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="contribution_scores_{start}_{end}.csv"'
        )
        return response
