from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .events import RequestEvent, MessageEvent

channel_layer = get_channel_layer()


def send_event_request(event_request):
    _send_realtime_event_to_user(
        to_user_ids=[event_request.to_user.id],
        realtime_event=RequestEvent(
            event=event_request.event.id,
            from_user=event_request.from_user.id,
            to_user=event_request.to_user.id,
            decision=event_request.decision,
            created=event_request.created,
        )
    )


def send_message(message, chat_members):
    _send_realtime_event_to_user(
        to_user_ids=chat_members,
        realtime_event=MessageEvent(
            from_user=message.from_user_id,
            text=message.text,
            created=message.created,
            chat=message.chat.id,
        )
    )


def _send_realtime_event_to_user(to_user_ids, realtime_event):
    async_to_sync(channel_layer.send)(
        'realtime-event-sender',
        {
            'type': 'send_event',
            'to_user_ids': to_user_ids,
            'realtime_event_dict': realtime_event.properties_dict,
        }
    )
