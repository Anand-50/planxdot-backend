from django.urls import path
from .views import (
    admin_dashboard,
    analytics_overview,
    funnel_analytics,
    list_reports,
    suspend_user,
    update_report_status,
    update_subscription,
    update_post_status,
    force_disable_nda,
    view_nda_acceptances,
    view_report
)

urlpatterns = [
    path("users/<uuid:user_id>/status/", suspend_user),
    path("users/<uuid:user_id>/subscription/", update_subscription),

    path("posts/<uuid:post_id>/status/", update_post_status),
    path("posts/<uuid:post_id>/disable-nda/", force_disable_nda),
    path("posts/<uuid:post_id>/nda-logs/", view_nda_acceptances),
    path("dashboard/", admin_dashboard),
    
    path("reports/", list_reports),
    path("reports/<uuid:report_id>/", view_report),
    path("reports/<uuid:report_id>/status/", update_report_status),

    path("analytics/overview/", analytics_overview),
    path("analytics/funnel/", funnel_analytics),
]
