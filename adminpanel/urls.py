from django.urls import path
from .views import (
    suspend_user,
    update_subscription,
    update_post_status,
    force_disable_nda,
    view_nda_acceptances
)

urlpatterns = [
    path("users/<uuid:user_id>/status/", suspend_user),
    path("users/<uuid:user_id>/subscription/", update_subscription),

    path("posts/<uuid:post_id>/status/", update_post_status),
    path("posts/<uuid:post_id>/disable-nda/", force_disable_nda),
    path("posts/<uuid:post_id>/nda-logs/", view_nda_acceptances),
]
