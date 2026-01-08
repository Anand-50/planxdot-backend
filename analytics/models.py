import uuid
from django.db import models


# =========================
# CORE EVENT LOG
# =========================
class AnalyticsEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user_id = models.UUIDField(null=True)
    role = models.CharField(max_length=20, null=True)

    event_type = models.CharField(max_length=50)
    target_type = models.CharField(max_length=50, null=True)
    target_id = models.UUIDField(null=True)

    metadata = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True)
    device_info = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_events"


# =========================
# FUNNEL TRACKING
# =========================
class AnalyticsFunnel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user_id = models.UUIDField()
    role = models.CharField(max_length=20)

    step = models.CharField(max_length=50)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_funnel"


# =========================
# POST ENGAGEMENT
# =========================
class AnalyticsPostEngagement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    post_id = models.UUIDField()
    user_id = models.UUIDField()

    action = models.CharField(max_length=20)  # view / like / save / share
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_post_engagement"


# =========================
# PROFILE VIEWS
# =========================
class AnalyticsProfileView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    viewer_id = models.UUIDField()
    profile_owner_id = models.UUIDField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_profile_views"


# =========================
# CHAT METRICS
# =========================
class AnalyticsChatMetric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    thread_id = models.UUIDField()
    sender_id = models.UUIDField()
    message_type = models.CharField(max_length=20)  # text / file / voice

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_chat_metrics"


# =========================
# PAYMENTS
# =========================
class AnalyticsPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user_id = models.UUIDField()
    plan_name = models.CharField(max_length=50)
    amount = models.IntegerField()
    status = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_payments"


# =========================
# RISK SIGNALS
# =========================
class AnalyticsRiskSignal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user_id = models.UUIDField()
    signal_type = models.CharField(max_length=50)
    severity = models.IntegerField()
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_risk_signals"
