from django.contrib import admin

from .models import Task, TaskCategory, TaskEvidence


class TaskEvidenceInline(admin.TabularInline):
    model = TaskEvidence
    extra = 0
    readonly_fields = ('uploaded_at',)
    fields = ('file', 'file_name', 'description', 'uploaded_by', 'uploaded_at')


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'difficulty_level',
        'default_expected_output',
        'default_expected_duration_minutes',
        'active',
        'updated_at',
    )
    list_filter = ('difficulty_level', 'active')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'assigned_to',
        'supervisor',
        'category',
        'department',
        'status',
        'difficulty_level',
        'date_assigned',
        'due_date',
        'updated_at',
    )
    list_filter = (
        'status',
        'difficulty_level',
        'department',
        'category',
        'date_assigned',
    )
    search_fields = (
        'title',
        'description',
        'assigned_to__email',
        'assigned_to__first_name',
        'assigned_to__last_name',
        'supervisor__email',
    )
    autocomplete_fields = (
        'assigned_to',
        'assigned_by',
        'supervisor',
        'department',
        'category',
    )
    readonly_fields = (
        'submitted_at',
        'reviewed_at',
        'approved_at',
        'created_at',
        'updated_at',
    )
    inlines = [TaskEvidenceInline]
    date_hierarchy = 'date_assigned'
    ordering = ('-created_at',)

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'description',
                    'status',
                    'category',
                    'difficulty_level',
                    'department',
                )
            },
        ),
        (
            'People',
            {
                'fields': (
                    'assigned_to',
                    'assigned_by',
                    'supervisor',
                )
            },
        ),
        (
            'Schedule',
            {
                'fields': (
                    'date_assigned',
                    'due_date',
                    'date_performed',
                    'start_time',
                    'end_time',
                    'expected_duration_minutes',
                    'actual_duration_minutes',
                )
            },
        ),
        (
            'Output',
            {
                'fields': (
                    'expected_output',
                    'actual_output',
                    'challenges_encountered',
                    'user_comments',
                )
            },
        ),
        (
            'Supervisor review',
            {
                'fields': (
                    'supervisor_comments',
                    'supervisor_quality_rating',
                    'supervisor_accuracy_rating',
                    'supervisor_timeliness_rating',
                    'submitted_at',
                    'reviewed_at',
                    'approved_at',
                )
            },
        ),
        (
            'Timestamps',
            {'fields': ('created_at', 'updated_at')},
        ),
    )


@admin.register(TaskEvidence)
class TaskEvidenceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'task',
        'file_name',
        'uploaded_by',
        'uploaded_at',
    )
    list_filter = ('uploaded_at',)
    search_fields = ('file_name', 'description', 'task__title')
    autocomplete_fields = ('task', 'uploaded_by')
    readonly_fields = ('uploaded_at',)
