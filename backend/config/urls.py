"""
URL configuration for config project.

Phase 5: REST API under /api/ with JWT authentication.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    """Simple health check used to verify the Django server is running."""
    return JsonResponse(
        {
            'status': 'ok',
            'project': 'Activity-Based Performance Tracker',
            'phase': 6,
        }
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health, name='health'),
    path('api/', include('accounts.urls')),
    path('api/', include('departments.urls')),
    path('api/', include('tasks.urls')),
    path('api/', include('attendance.urls')),
    path('api/', include('performance.urls')),
    path('api/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
