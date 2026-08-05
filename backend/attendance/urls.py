from django.urls import include, path
from rest_framework.routers import DefaultRouter

from attendance.views import AttendanceRecordViewSet

router = DefaultRouter()
router.register('attendance', AttendanceRecordViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]
