from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .events import CreatedRequestEvent

channel_layer = get_channel_layer()


def send_event_request(event_request):
    _send_realtime_event_to_user(
        user=event_request.to_user,
        realtime_event=CreatedRequestEvent(
            sender_id=event_request.from_user.id,
        )
    )


def _send_realtime_event_to_user(user, realtime_event):
    async_to_sync(channel_layer.send)(
        'realtime-event-sender',
        {
            'type': 'send_event',
            'user_id_str': str(user.id),
            'realtime_event_dict': realtime_event.properties_dict,
        }
    )
