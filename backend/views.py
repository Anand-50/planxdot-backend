def home(request):
    return JsonResponse({
        "status": "Backend running",
        "service": "planXdot API"
    })
