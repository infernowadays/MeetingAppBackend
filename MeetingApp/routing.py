from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

from realtime.websocket.routing import websocket_urlpatterns
from realtime.websocket.token_auth import TokenAuthMiddlewareStack
from realtime import consumers

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
    'channel': ChannelNameRouter({
        'realtime-event-sender': consumers.EventSenderConsumer,
    }),
})
