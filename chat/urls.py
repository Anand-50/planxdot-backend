from django.urls import path
from .views import (
    send_connection_request,
    respond_connection,
    send_message,
    list_messages,
    clear_chat,
    report_message,
    update_chat_settings
)

urlpatterns = [
    path("connect/<uuid:receiver_id>/", send_connection_request),
    path("connect/respond/<uuid:connection_id>/", respond_connection),

    path("threads/<uuid:thread_id>/send/", send_message),
    path("threads/<uuid:thread_id>/messages/", list_messages),
    path("threads/<uuid:thread_id>/clear/", clear_chat),

    path("message/<uuid:message_id>/report/", report_message),
    path("settings/", update_chat_settings),
]
