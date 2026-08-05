from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import (
    ChangePasswordView,
    EmailTokenObtainPairView,
    MeView,
    RegisterView,
    TokenRefreshAPIView,
    UserViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', EmailTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/token/refresh/', TokenRefreshAPIView.as_view(), name='auth-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('', include(router.urls)),
]
