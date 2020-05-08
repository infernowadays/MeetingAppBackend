from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('messages/<int:event_id>', csrf_exempt(MessageView.as_view())),
    path('messages', csrf_exempt(MessageView.as_view())),

    path('private-messages/<int:user_id>', csrf_exempt(PrivateMessageView.as_view())),
    path('private-messages', csrf_exempt(PrivateMessageView.as_view())),
]
