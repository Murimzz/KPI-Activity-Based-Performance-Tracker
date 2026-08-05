from django.contrib import admin

from .models import KPIWeight, PerformanceSnapshot


@admin.register(KPIWeight)
class KPIWeightAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'metric_key',
        'weight_percentage',
        'active',
        'updated_at',
    )
    list_filter = ('active',)
    search_fields = ('name', 'metric_key')
    ordering = ('metric_key',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PerformanceSnapshot)
class PerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'period_type',
        'period_start',
        'period_end',
        'overall_activity_score',
        'approved_tasks',
        'pending_tasks',
        'rejected_tasks',
        'created_at',
    )
    list_filter = ('period_type', 'period_start')
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
    )
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'period_start'
    ordering = ('-period_end',)
