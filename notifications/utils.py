from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

async_to_sync(channel_layer.group_send)(
    f'notify_{user_id}',
    {
        "type": "notify",
        "data": {
            "title": title,
            "message": message,
            "type": notif_type
        }
    }
)
