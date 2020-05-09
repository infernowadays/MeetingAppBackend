from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('chats', csrf_exempt(ChatsView.as_view())),

    path('messages/<int:event_id>', csrf_exempt(MessageView.as_view())),
    path('messages', csrf_exempt(MessageView.as_view())),

    path('private-messages/<int:user_id>', csrf_exempt(PrivateMessageView.as_view())),
    path('private-messages', csrf_exempt(PrivateMessageView.as_view())),
]
