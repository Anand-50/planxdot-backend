from django.urls import path
from .views import create_post, feed, accept_nda, view_post, discovery_feed, discovery_with_filters, engage_post, track_view, report_post, post_engagement_counts

urlpatterns = [
    path('create/', create_post),
    path('feed/', feed),
    path('<uuid:post_id>/accept-nda/', accept_nda),
    path('<uuid:post_id>/', view_post),
    path("discover/", discovery_feed),
    path("discover/filter/", discovery_with_filters),
    path("<uuid:post_id>/engage/", engage_post),
    path("<uuid:post_id>/view/", track_view),
    path("<uuid:post_id>/report/", report_post),
    path("<uuid:post_id>/engagements/", post_engagement_counts),
]
