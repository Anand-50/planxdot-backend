import uuid
from django.db import models


class AdminUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=50,
        choices=[
            ('super_admin', 'Super Admin'),
            ('operations_admin', 'Operations Admin'),
            ('fraud_team', 'Fraud Team'),
            ('support', 'Support'),
            ('moderator', 'Moderator'),
            ('ads_manager', 'Ads Manager'),
            ('analytics', 'Analytics'),
        ]
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_users'


class AdminAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    admin = models.ForeignKey(
        AdminUser,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50)
    target_id = models.UUIDField()

    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_audit_logs'
