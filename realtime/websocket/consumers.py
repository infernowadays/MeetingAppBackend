import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .utils import construct_group_name_from_uid


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the user object (provided by the TokenAuthMiddleware in MeetingApp/routing.py)
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()

        self.user_group_name = construct_group_name_from_uid(self.user.id)

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name  # I believe 'channel_name' is a unique name given per Consumer instance
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        await self.close()

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        data_serialized = json.loads(text_data)
        # print(data_serialized)

    async def request_event(self, message):
        await self._send_consumer_event_to_client(
            event=message
        )

    async def message_event(self, message):
        await self._send_consumer_event_to_client(
            event=message
        )

    # The following is called by the CONSUMER to send the message to the CLIENT
    async def _send_consumer_event_to_client(self, event):
        await self.send(text_data=json.dumps(event))
