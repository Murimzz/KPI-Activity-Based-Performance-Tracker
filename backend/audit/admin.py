from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'timestamp',
        'user',
        'action',
        'model_name',
        'object_id',
    )
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = (
        'action',
        'model_name',
        'object_id',
        'description',
        'user__email',
    )
    autocomplete_fields = ('user',)
    readonly_fields = (
        'user',
        'action',
        'model_name',
        'object_id',
        'description',
        'timestamp',
    )
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
