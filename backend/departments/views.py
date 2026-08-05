from rest_framework import viewsets

from accounts.permissions import IsAdminOrReadOnly
from audit.services import log_action
from departments.models import Department
from departments.serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'created_at')
    ordering = ('name',)

    def perform_create(self, serializer):
        dept = serializer.save()
        log_action(
            action='CREATE',
            model_name='Department',
            object_id=dept.id,
            description=f'Department created: {dept.name}',
            user=self.request.user,
        )

    def perform_update(self, serializer):
        dept = serializer.save()
        log_action(
            action='UPDATE',
            model_name='Department',
            object_id=dept.id,
            description=f'Department updated: {dept.name}',
            user=self.request.user,
        )

    def perform_destroy(self, instance):
        log_action(
            action='DELETE',
            model_name='Department',
            object_id=instance.id,
            description=f'Department deleted: {instance.name}',
            user=self.request.user,
        )
        instance.delete()
