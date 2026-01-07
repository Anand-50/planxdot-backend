from .models import Notification

def create_notification(
    user_id,
    notif_type,
    title,
    message,
    reference_type=None,
    reference_id=None
):
    Notification.objects.create(
        user_id=user_id,
        type=notif_type,
        title=title,
        message=message,
        reference_type=reference_type,
        reference_id=reference_id
    )
