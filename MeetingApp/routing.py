from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

from realtime.websocket.routing import websocket_urlpatterns
from realtime.websocket.token_auth import token_auth_middleware_stack
from realtime import consumers

application = ProtocolTypeRouter({
    'websocket': token_auth_middleware_stack(
        URLRouter(websocket_urlpatterns)
    ),
    'channel': ChannelNameRouter({
        'realtime-event-sender': consumers.EventSenderConsumer,
    }),
})
