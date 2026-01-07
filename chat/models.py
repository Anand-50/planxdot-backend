import uuid
from django.db import models
from accounts.models import User


class Connection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_requests"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_requests"
    )

    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "pending"),
            ("accepted", "accepted"),
            ("rejected", "rejected"),
            ("blocked", "blocked"),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "connections"


class ChatThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    connection = models.OneToOneField(
        Connection, on_delete=models.CASCADE
    )

    is_frozen = models.BooleanField(default=False)
    frozen_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_threads"


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    thread = models.ForeignKey(
        ChatThread, on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    message_type = models.CharField(
        max_length=20,
        choices=[
            ("text", "text"),
            ("file", "file"),
            ("voice", "voice"),
            ("image", "image"),
        ],
    )

    content = models.TextField(null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"


class ChatReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    message = models.ForeignKey(
        ChatMessage, on_delete=models.CASCADE
    )
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    reason = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        default="open",
        choices=[
            ("open", "open"),
            ("under_review", "under_review"),
            ("resolved", "resolved"),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_reports"


class UserChatSettings(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )

    mute_notifications = models.BooleanField(default=False)

    class Meta:
        db_table = "user_chat_settings"
