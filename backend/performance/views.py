from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models.functions import TruncWeek, TruncMonth
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from accounts.permissions import IsAdminRole, IsSupervisorOrAdmin
from performance.models import KPIWeight, PeriodType
from performance.serializers import KPIWeightSerializer
from performance.services import (
    build_user_performance_metrics,
    create_or_update_performance_snapshot,
)
from tasks.models import Task, TaskStatus

User = get_user_model()


def _parse_date_range(request):
    today = timezone.localdate()
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    if start and end:
        from datetime import date as date_cls

        return date_cls.fromisoformat(start), date_cls.fromisoformat(end)
    return today - timedelta(days=30), today


def _target_user(request):
    user_id = request.query_params.get('user_id')
    if user_id:
        if (
            request.user.role not in (UserRole.ADMIN, UserRole.SUPERVISOR)
            and not request.user.is_superuser
            and str(request.user.id) != str(user_id)
        ):
            return None, Response(
                {'detail': 'Not allowed to view this user.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            return User.objects.get(pk=user_id), None
        except User.DoesNotExist:
            return None, Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
    return request.user, None


class KPIWeightViewSet(viewsets.ModelViewSet):
    queryset = KPIWeight.objects.all()
    serializer_class = KPIWeightSerializer
    filterset_fields = ('active', 'metric_key')
    ordering = ('metric_key',)
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminRole()]


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target, err = _target_user(request)
        if err:
            return err
        start, end = _parse_date_range(request)
        metrics = build_user_performance_metrics(target, start, end)
        recent = (
            Task.objects.filter(assigned_to=target)
            .select_related('category')
            .order_by('-updated_at')[:10]
        )
        from tasks.serializers import TaskSerializer

        return Response(
            {
                'user_id': target.id,
                'period_start': start,
                'period_end': end,
                'metrics': metrics,
                'recent_tasks': TaskSerializer(recent, many=True).data,
                'disclaimer': (
                    'Overall Activity Score is a Contribution Score, '
                    'not an official government performance appraisal.'
                ),
            }
        )


class DashboardWeeklyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target, err = _target_user(request)
        if err:
            return err
        end = timezone.localdate()
        start = end - timedelta(days=7)
        metrics = build_user_performance_metrics(target, start, end)
        create_or_update_performance_snapshot(
            target, PeriodType.WEEKLY, start, end
        )
        return Response({'period_start': start, 'period_end': end, 'metrics': metrics})


class DashboardMonthlyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target, err = _target_user(request)
        if err:
            return err
        end = timezone.localdate()
        start = end.replace(day=1)
        metrics = build_user_performance_metrics(target, start, end)
        create_or_update_performance_snapshot(
            target, PeriodType.MONTHLY, start, end
        )
        return Response({'period_start': start, 'period_end': end, 'metrics': metrics})


class DashboardTeamSummaryView(APIView):
    permission_classes = [IsSupervisorOrAdmin]

    def get(self, request):
        start, end = _parse_date_range(request)
        user = request.user
        if user.role == UserRole.ADMIN or user.is_superuser:
            team = User.objects.filter(
                role__in=(UserRole.INTERN, UserRole.STAFF, UserRole.SUPERVISOR)
            )
        else:
            team = User.objects.filter(supervisor=user)

        results = []
        for member in team:
            metrics = build_user_performance_metrics(member, start, end)
            results.append(
                {
                    'user': {
                        'id': member.id,
                        'email': member.email,
                        'full_name': member.get_full_name(),
                        'role': member.role,
                    },
                    'metrics': metrics,
                }
            )
        return Response(
            {
                'period_start': start,
                'period_end': end,
                'team_size': len(results),
                'members': results,
                'disclaimer': (
                    'Scores are Contribution / Activity Performance Scores only.'
                ),
            }
        )
