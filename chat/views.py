import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

from accounts.utils import get_user_from_token
from accounts.models import User

from .models import (
    Connection,
    ChatThread,
    ChatMessage,
    ChatReport,
    UserChatSettings
)




@csrf_exempt
def send_connection_request(request, receiver_id):
    sender = get_user_from_token(request)

    if sender.id == receiver_id:
        return JsonResponse({"error": "Invalid request"}, status=400)

    exists = Connection.objects.filter(
        requester_id=sender.id,
        receiver_id=receiver_id
    ).exists()

    if exists:
        return JsonResponse({"error": "Request already sent"}, status=400)

    Connection.objects.create(
        requester_id=sender.id,
        receiver_id=receiver_id
    )

    return JsonResponse({"message": "Connection request sent"})


@csrf_exempt
def respond_connection(request, connection_id):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    action = data.get("action")  # accepted / rejected

    connection = Connection.objects.filter(
        id=connection_id,
        receiver_id=user.id
    ).first()

    if not connection:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    connection.status = action
    connection.responded_at = now()
    connection.save()

    if action == "accepted":
        ChatThread.objects.create(connection=connection)

    return JsonResponse({"message": f"Connection {action}"})


@csrf_exempt
def send_message(request, thread_id):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    thread = ChatThread.objects.filter(id=thread_id).first()

    if not thread:
        return JsonResponse({"error": "Invalid thread"}, status=404)

    if thread.is_frozen:
        return JsonResponse({"error": "Chat frozen"}, status=403)

    connection = thread.connection
    if user.id not in [connection.requester_id, connection.receiver_id]:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    ChatMessage.objects.create(
        thread=thread,
        sender_id=user.id,
        message_type=data["message_type"],  # text / file / voice / image
        content=data.get("content"),
        file_name=data.get("file_name"),
        file_type=data.get("file_type")
    )

    return JsonResponse({"message": "Message sent"})


def list_messages(request, thread_id):
    user = get_user_from_token(request)

    thread = ChatThread.objects.filter(id=thread_id).first()
    if not thread:
        return JsonResponse({"error": "Invalid thread"}, status=404)

    connection = thread.connection
    if user.id not in [connection.requester_id, connection.receiver_id]:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    messages = ChatMessage.objects.filter(
        thread=thread,
        is_deleted=False
    ).order_by("created_at")

    data = [{
        "id": str(m.id),
        "sender_id": str(m.sender_id),
        "type": m.message_type,
        "content": m.content,
        "created_at": m.created_at
    } for m in messages]

    return JsonResponse(data, safe=False)

@csrf_exempt
def clear_chat(request, thread_id):
    user = get_user_from_token(request)

    thread = ChatThread.objects.filter(id=thread_id).first()
    if not thread:
        return JsonResponse({"error": "Invalid thread"}, status=404)

    ChatMessage.objects.filter(
        thread=thread,
        sender_id=user.id
    ).update(is_deleted=True)

    return JsonResponse({"message": "Chat cleared (local)"})


@csrf_exempt
def report_message(request, message_id):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    ChatReport.objects.create(
        message_id=message_id,
        reporter_id=user.id,
        reason=data["reason"],
        description=data.get("description")
    )

    return JsonResponse({"message": "Report submitted"})


@csrf_exempt
def update_chat_settings(request):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    settings, _ = UserChatSettings.objects.get_or_create(user_id=user.id)
    settings.mute_notifications = data.get("mute", False)
    settings.save()

    return JsonResponse({"message": "Settings updated"})
