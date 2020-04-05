from channels.routing import ProtocolTypeRouter, URLRouter

from chat.routing import websocket_urlpatterns
from chat.token_auth import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
