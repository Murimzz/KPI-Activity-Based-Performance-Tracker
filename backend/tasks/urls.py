from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tasks.views import TaskCategoryViewSet, TaskViewSet

router = DefaultRouter()
router.register('task-categories', TaskCategoryViewSet, basename='task-category')
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
