from django.urls import include, path
from rest_framework.routers import DefaultRouter

from performance.views import (
    DashboardMonthlyView,
    DashboardSummaryView,
    DashboardTeamSummaryView,
    DashboardWeeklyView,
    KPIWeightViewSet,
)

router = DefaultRouter()
router.register('kpi-weights', KPIWeightViewSet, basename='kpi-weight')

urlpatterns = [
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/weekly/', DashboardWeeklyView.as_view(), name='dashboard-weekly'),
    path('dashboard/monthly/', DashboardMonthlyView.as_view(), name='dashboard-monthly'),
    path(
        'dashboard/team-summary/',
        DashboardTeamSummaryView.as_view(),
        name='dashboard-team-summary',
    ),
    path('', include(router.urls)),
]
