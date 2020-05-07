from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('chats/<int:pk>', csrf_exempt(ChatView.as_view())),
    path('messages', csrf_exempt(MessageView.as_view())),
]
