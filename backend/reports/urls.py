from django.urls import path

from reports.views import (
    CategoryBreakdownView,
    ExportCSVView,
    MonthlyReportView,
    StatusBreakdownView,
    UserReportView,
    WeeklyReportView,
)

urlpatterns = [
    path('reports/user/<int:user_id>/', UserReportView.as_view(), name='report-user'),
    path('reports/weekly/', WeeklyReportView.as_view(), name='report-weekly'),
    path('reports/monthly/', MonthlyReportView.as_view(), name='report-monthly'),
    path(
        'reports/category-breakdown/',
        CategoryBreakdownView.as_view(),
        name='report-category-breakdown',
    ),
    path(
        'reports/status-breakdown/',
        StatusBreakdownView.as_view(),
        name='report-status-breakdown',
    ),
    path('reports/export/csv/', ExportCSVView.as_view(), name='report-export-csv'),
]
