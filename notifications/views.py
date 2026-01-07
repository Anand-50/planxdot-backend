from accounts.utils import get_user_from_token
from django.http import JsonResponse

def my_notifications(request):
    user = get_user_from_token(request)

    notifications = Notification.objects.filter(
        user_id=user.id,
        is_hidden=False
    ).order_by("-created_at")

    data = [{
        "id": str(n.id),
        "type": n.type,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at,
        "reference": {
            "type": n.reference_type,
            "id": str(n.reference_id) if n.reference_id else None
        }
    } for n in notifications]

    return JsonResponse(data, safe=False)


from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def mark_notification_read(request):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    Notification.objects.filter(
        id=data["notification_id"],
        user_id=user.id
    ).update(is_read=True)

    return JsonResponse({"message": "Marked as read"})


@csrf_exempt
def hide_notification(request):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    Notification.objects.filter(
        id=data["notification_id"],
        user_id=user.id
    ).update(is_hidden=True)

    return JsonResponse({"message": "Notification hidden"})
