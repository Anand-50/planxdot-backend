import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.utils import get_user_from_token
from reports.models import Report


@csrf_exempt
def create_report(request):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    Report.objects.create(
        reporter_id=user.id,
        reported_user_id=data.get("reported_user_id"),
        target_type=data["target_type"],
        target_id=data["target_id"],
        reason=data["reason"],
        description=data.get("description", "")
    )

    return JsonResponse({"message": "Report submitted"})
