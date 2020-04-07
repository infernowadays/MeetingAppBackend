import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer

from .utils import construct_group_name_from_id
from channels.layers import get_channel_layer
from chat.messaging import send_event_via_websocket_group_consumer
from asgiref.sync import async_to_sync



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.room_group_name = 'chat_%s' % self.room_name

        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()

        self.user_group_name = construct_group_name_from_id(self.user.id)
        # Join room group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.user_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # Receive accepted_friend_request from room group and send down to client(s)
    async def accepted_friend_request(self, message):
        print("Consumer: accepted_friend_request")
        await self._send_consumer_event_to_client(
            event=message
        )

    # Receive created_friend_request from room group and send down to client(s)
    async def created_friend_request(self, message):
        print("Consumer: created_friend_request")
        print(message)
        await self._send_consumer_event_to_client(
            event=message
        )

    # Receive rejected_friend_request from room group and send down to client(s)
    async def rejected_friend_request(self, message):
        print("Consumer: rejected_friend_request")
        await self._send_consumer_event_to_client(
            event=message
        )

    # Receive canceled_friend_request from room group and send down to client(s)
    async def canceled_friend_request(self, message):
        print("Consumer: canceled_friend_request")
        await self._send_consumer_event_to_client(
            event=message
        )

    # The following is called by the CONSUMER to send the message to the CLIENT
    async def _send_consumer_event_to_client(self, event):
        await self.send(text_data=json.dumps(event))


class EventSenderConsumer(AsyncConsumer):

    async def send_event(self, message):
        print("\n\n\n\n\n\n\n\n\\n\n\nlalalalal")
        try:
            user = await database_sync_to_async(get_user_object)(id=message['user_uuid_str'])
        except NotFound:
            return

        await send_event_via_websocket_group_consumer(
            channel_layer=self.channel_layer,
            user=user
        )
        # # if check_if_websocket_is_active(user):
        #     print("Realtime: event_sender_consumer_send_event - websocket branch")
        #     await send_event_via_websocket_group_consumer(
        #         channel_layer=self.channel_layer,
        #         user=user,
        #         realtime_event_dict=message['realtime_event_dict']
        #     )
        # else:
        #     print("Realtime: event_sender_consumer_send_event - firebase branch")
        #     send_event_via_fcm(user, message['realtime_event_dict'])