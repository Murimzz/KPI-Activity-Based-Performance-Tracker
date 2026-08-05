from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Immutable-style audit trail for important actions."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=100, db_index=True)
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit log'
        verbose_name_plural = 'Audit logs'
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        actor = self.user.email if self.user_id else 'system'
        return f'{self.timestamp:%Y-%m-%d %H:%M} {actor} {self.action} {self.model_name}'
