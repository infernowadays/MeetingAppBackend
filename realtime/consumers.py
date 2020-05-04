from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from token_auth.models import UserProfile
from .websocket.messaging import send_event_via_websocket_group_consumer


# Used when we have to send a realtime event from inside sync code and we don't want it to block (like in a Django View)
class EventSenderConsumer(AsyncConsumer):

    async def send_event(self, message):
        user = await database_sync_to_async(UserProfile.objects.get)(id=(message['user_id_str']))

        await send_event_via_websocket_group_consumer(
            channel_layer=self.channel_layer,
            user=user,
            realtime_event_dict=message['realtime_event_dict']
        )
