from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from adminpanel.utils import get_admin_from_token
from adminpanel.models import AdminAuditLog
from accounts.models import User
from posts.models import Post, PostNDA
from subscriptions.models import Subscription
from django.utils.timezone import now
import json
from datetime import timedelta


@csrf_exempt
def suspend_user(request, user_id):
    admin = get_admin_from_token(request)
    data = json.loads(request.body)

    suspend = data.get("suspend")  # true / false
    reason = data.get("reason")

    User.objects.filter(id=user_id).update(
        is_suspended=suspend,
        suspended_reason=reason if suspend else None,
        suspended_at=now() if suspend else None
    )

    AdminAuditLog.objects.create(
        admin_id=admin.id,
        action="USER_SUSPENDED" if suspend else "USER_REACTIVATED",
        target_type="user",
        target_id=user_id,
        reason=reason
    )

    return JsonResponse({"message": "User status updated"})



@csrf_exempt
def update_subscription(request, user_id):
    admin = get_admin_from_token(request)
    data = json.loads(request.body)

    days = int(data.get("extend_days", 0))
    reason = data.get("reason")

    sub = Subscription.objects.filter(
        user_id=user_id,
        status="active"
    ).first()

    if not sub:
        return JsonResponse({"error": "No active subscription"}, status=404)

    sub.end_date += timedelta(days=days)
    sub.save()

    AdminAuditLog.objects.create(
        admin_id=admin.id,
        action="SUBSCRIPTION_EXTENDED",
        target_type="subscription",
        target_id=sub.id,
        reason=reason
    )

    return JsonResponse({"message": "Subscription updated"})


@csrf_exempt
def update_post_status(request, post_id):
    admin = get_admin_from_token(request)
    data = json.loads(request.body)

    status = data.get("status")  # paused / active / removed
    reason = data.get("reason")

    Post.objects.filter(id=post_id).update(status=status)

    AdminAuditLog.objects.create(
        admin_id=admin.id,
        action="POST_STATUS_CHANGE",
        target_type="post",
        target_id=post_id,
        reason=reason
    )

    return JsonResponse({"message": "Post updated"})


@csrf_exempt
def force_disable_nda(request, post_id):
    admin = get_admin_from_token(request)
    data = json.loads(request.body)

    reason = data.get("reason")

    PostNDA.objects.filter(post_id=post_id).update(is_active=False)
    Post.objects.filter(id=post_id).update(nda_required=False)

    AdminAuditLog.objects.create(
        admin_id=admin.id,
        action="NDA_DISABLED",
        target_type="post",
        target_id=post_id,
        reason=reason
    )

    return JsonResponse({"message": "NDA disabled"})


def view_nda_acceptances(request, post_id):
    admin = get_admin_from_token(request)

    records = NDAAcceptance.objects.filter(post_id=post_id)

    data = list(records.values(
        "viewer_id",
        "accepted_at",
        "viewer_ip",
        "viewer_device"
    ))

    return JsonResponse(data, safe=False)



@csrf_exempt
def freeze_chat(request, thread_id):
    admin = get_admin_from_token(request)
    data = json.loads(request.body)

    ChatThread.objects.filter(id=thread_id).update(
        is_frozen=True,
        frozen_reason=data.get("reason")
    )

    AdminAuditLog.objects.create(
    admin_id=admin.id,
    action="CHAT_FROZEN",
    target_type="chat_thread",
    target_id=thread_id,
    reason=data.get("reason")
)


    return JsonResponse({"message": "Chat frozen"})
