from .utils import construct_group_name_from_uid


async def send_event_via_websocket_group_consumer(channel_layer, to_user_ids, realtime_event_dict):
    for to_user_id in to_user_ids:
        group_name = construct_group_name_from_uid(to_user_id)
        await channel_layer.group_send(
            group=group_name,
            message=realtime_event_dict,
        )
