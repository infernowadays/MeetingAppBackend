# realtime/websocket/messaging.py
from .utils import construct_group_name_from_id


async def send_event_via_websocket_group_consumer(channel_layer, user):
    group_name = construct_group_name_from_id(user.id)

    await channel_layer.group_send(
        group=group_name,
        message="realtime_event_dict",
    )