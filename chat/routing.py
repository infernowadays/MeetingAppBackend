from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # (?P<room_name>\w+)/
    re_path(r'ws/chat/$', consumers.ChatConsumer),
]
