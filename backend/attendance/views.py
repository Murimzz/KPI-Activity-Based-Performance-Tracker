from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import UserRole
from accounts.permissions import IsSupervisorOrAdmin
from attendance.models import AttendanceRecord
from attendance.serializers import AttendanceRecordSerializer
from audit.services import log_action


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ('user', 'status', 'date')
    search_fields = ('notes', 'user__email')
    ordering_fields = ('date', 'created_at')
    ordering = ('-date',)
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = AttendanceRecord.objects.select_related('user')
        if user.role == UserRole.ADMIN or user.is_superuser:
            return qs
        if user.role == UserRole.SUPERVISOR:
            return qs.filter(user__supervisor=user) | qs.filter(user=user)
        return qs.filter(user=user)

    def get_permissions(self):
        if self.action in ('create', 'partial_update', 'update'):
            # Staff can create own; supervisors/admins can manage team
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        target = serializer.validated_data.get('user')
        if target is None:
            record = serializer.save(user=user)
        elif (
            target.id != user.id
            and user.role not in (UserRole.ADMIN, UserRole.SUPERVISOR)
            and not user.is_superuser
        ):
            raise PermissionError('Cannot create attendance for another user.')
        else:
            record = serializer.save()
        log_action(
            action='CREATE',
            model_name='AttendanceRecord',
            object_id=record.id,
            description=f'Attendance {record.date} for {record.user_id}',
            user=user,
        )

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except PermissionError as exc:
            from rest_framework.response import Response
            from rest_framework import status

            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
