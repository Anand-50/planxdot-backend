from django.utils.timezone import now
from subscriptions.models import Subscription
from accounts.models import User

from django.http import JsonResponse

class SubscriptionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        expired = Subscription.objects.filter(
            end_date__lt=now().date(),
            status="active"
        )

        for sub in expired:
            sub.status = "expired"
            sub.save()
            User.objects.filter(id=sub.user_id).update(
                subscription_status="expired"
            )

        return self.get_response(request)




class SuspensionMiddleware:
    """
    Blocks all API access for suspended users.
    Applies globally to all authenticated user requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user = getattr(request, "user", None)

        # If user is authenticated AND suspended → block
        if user and user.is_authenticated:
            if getattr(user, "is_suspended", False):
                return JsonResponse(
                    {
                        "error": "Account suspended",
                        "reason": getattr(user, "suspended_reason", None)
                    },
                    status=403
                )

        return self.get_response(request)
