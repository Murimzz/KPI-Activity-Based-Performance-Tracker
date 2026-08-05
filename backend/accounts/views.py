from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.models import UserRole
from accounts.permissions import IsAdminRole, IsSupervisorOrAdmin
from accounts.serializers import (
    ChangePasswordSerializer,
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from audit.services import log_action

User = get_user_model()


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(
            action='REGISTER',
            model_name='User',
            object_id=user.id,
            description=f'User registered: {user.email}',
            user=user,
        )


class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_action(
            action='CHANGE_PASSWORD',
            model_name='User',
            object_id=request.user.id,
            description='Password changed',
            user=request.user,
        )
        return Response({'detail': 'Password updated successfully.'})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('department', 'supervisor').all()
    filterset_fields = ('role', 'department', 'supervisor', 'is_active')
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'employee_or_intern_number',
    )
    ordering_fields = ('last_name', 'first_name', 'date_joined', 'email')
    ordering = ('last_name', 'first_name')

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'my_team'):
            return [IsAuthenticated()]
        return [IsAdminRole()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == UserRole.ADMIN or user.is_superuser:
            return qs
        if user.role == UserRole.SUPERVISOR:
            return (qs.filter(supervisor=user) | qs.filter(pk=user.pk)).distinct()
        return qs.filter(pk=user.pk)

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(
            action='CREATE',
            model_name='User',
            object_id=user.id,
            description=f'User created: {user.email}',
            user=self.request.user,
        )

    def perform_update(self, serializer):
        user = serializer.save()
        log_action(
            action='UPDATE',
            model_name='User',
            object_id=user.id,
            description=f'User updated: {user.email}',
            user=self.request.user,
        )

    def perform_destroy(self, instance):
        log_action(
            action='DELETE',
            model_name='User',
            object_id=instance.id,
            description=f'User deactivated/deleted: {instance.email}',
            user=self.request.user,
        )
        # Soft-deactivate instead of hard delete when possible
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])

    @action(detail=False, methods=['get'], url_path='my-team')
    def my_team(self, request):
        user = request.user
        if user.role == UserRole.ADMIN or user.is_superuser:
            qs = User.objects.exclude(role=UserRole.ADMIN)
        elif user.role == UserRole.SUPERVISOR:
            qs = User.objects.filter(supervisor=user)
        else:
            return Response(
                {'detail': 'Only supervisors and admins can view a team.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = qs.select_related('department', 'supervisor')
        page = self.paginate_queryset(qs)
        serializer = UserSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


# Re-export refresh view for urls clarity
TokenRefreshAPIView = TokenRefreshView
