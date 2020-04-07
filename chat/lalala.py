import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer

from .utils import construct_group_name_from_id
from channels.layers import get_channel_layer
from chat.messaging import send_event_via_websocket_group_consumer
from asgiref.sync import async_to_sync


def send_accepted_friend_request(user, other_user):
    _send_realtime_event_to_user(
        user=user,
        other_user=other_user
    )


def _send_realtime_event_to_user(user, other_user):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        "realtime-event-sender",
        {
            'type': 'send_event',
            'user_uuid_str': str(user.id),
            'other_user_uuid_str': str(other_user.id),
        }
    )
