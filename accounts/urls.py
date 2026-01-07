from django.urls import path
from .views import register, verify_email, verify_phone, login,dashboard, my_profile,  update_profile, update_settings, my_posts, my_nda_acceptances, my_connections, deactivate_account, request_deletion

urlpatterns = [
    path('register/', register),
    path('verify-email/', verify_email),
    path('verify-phone/', verify_phone),
    path('login/', login),
    path("dashboard/", dashboard),
    path("profile/", my_profile),
    path("profile/update/", update_profile),

    path("settings/", update_settings),

    path("my-posts/", my_posts),
    path("my-nda/", my_nda_acceptances),
    path("my-connections/", my_connections),

    path("deactivate/", deactivate_account),
    path("request-deletion/", request_deletion),

]
