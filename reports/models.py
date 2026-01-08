import uuid
from django.db import models

class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    reporter_id = models.UUIDField()
    reported_user_id = models.UUIDField(null=True, blank=True)

    target_type = models.CharField(
        max_length=50,
        choices=[
            ('user', 'User'),
            ('post', 'Post'),
            ('chat', 'Chat'),
            ('nda', 'NDA'),
        ]
    )

    target_id = models.UUIDField()

    reason = models.CharField(
        max_length=100,
        choices=[
            ('fake_profile', 'Fake Profile'),
            ('idea_theft', 'Idea Theft'),
            ('harassment', 'Harassment'),
            ('spam', 'Spam'),
            ('fraud', 'Fraud'),
            ('nda_violation', 'NDA Violation'),
            ('other', 'Other'),
        ]
    )

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        default='open',
        choices=[
            ('open', 'Open'),
            ('under_review', 'Under Review'),
            ('resolved', 'Resolved'),
            ('archived', 'Archived'),
        ]
    )

    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
