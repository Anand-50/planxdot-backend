from django.utils.timezone import now
from analytics.models import (
    AnalyticsEvent,
    AnalyticsFunnel,
    AnalyticsPostEngagement,
    AnalyticsProfileView,
    AnalyticsChatMetric,
    AnalyticsPayment
)

def log_event(
    user_id=None,
    role=None,
    event_type=None,
    target_type=None,
    target_id=None,
    metadata=None,
    ip=None,
    device=None
):
    AnalyticsEvent.objects.create(
        user_id=user_id,
        role=role,
        event_type=event_type,
        target_type=target_type,
        target_id=target_id,
        metadata=metadata or {},
        ip_address=ip,
        device_info=device
    )


def log_funnel(user_id, role, step):
    AnalyticsFunnel.objects.create(
        user_id=user_id,
        role=role,
        step=step
    )
