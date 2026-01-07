import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import ChatThread, ChatMessage
from accounts.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        # Validate thread + permissions
        try:
            thread = ChatThread.objects.get(id=self.thread_id)
            conn = thread.connection
            if user.id not in [conn.requester_id, conn.receiver_id]:
                await self.close()
                return

            if thread.is_frozen:
                await self.close()
                return

        except ChatThread.DoesNotExist:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]

        message = data.get("message")
        msg_type = data.get("type", "text")

        # Save message (DB = source of truth)
        msg = ChatMessage.objects.create(
            thread_id=self.thread_id,
            sender_id=user.id,
            message_type=msg_type,
            content=message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": str(user.id),
                "created_at": str(msg.created_at)
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
