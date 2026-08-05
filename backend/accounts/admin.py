from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ('email',)
    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'employee_or_intern_number',
        'department',
        'supervisor',
        'is_active',
        'is_staff',
        'date_joined',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'department')
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'employee_or_intern_number',
        'phone_number',
    )
    readonly_fields = ('date_joined', 'created_at', 'updated_at', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Personal info'),
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'phone_number',
                    'employee_or_intern_number',
                )
            },
        ),
        (
            _('Organization'),
            {'fields': ('role', 'department', 'supervisor')},
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (
            _('Important dates'),
            {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'employee_or_intern_number',
                    'role',
                    'department',
                    'supervisor',
                    'phone_number',
                    'password1',
                    'password2',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )
    filter_horizontal = ('groups', 'user_permissions')
