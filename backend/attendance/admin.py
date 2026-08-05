from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'date',
        'status',
        'check_in_time',
        'check_out_time',
        'created_at',
    )
    list_filter = ('status', 'date')
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'notes',
    )
    autocomplete_fields = ('user',)
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)
