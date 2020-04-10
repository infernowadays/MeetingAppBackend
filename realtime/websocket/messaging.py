from .utils import construct_group_name_from_uid
# from token_auth.serializers import UserSerializer


async def send_event_via_websocket_group_consumer(channel_layer, user, realtime_event_dict):
    group_name = construct_group_name_from_uid(user.id)
    await channel_layer.group_send(
            group=group_name,
            message=realtime_event_dict,
        )
