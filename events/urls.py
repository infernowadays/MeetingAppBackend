from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import *


urlpatterns = [
    path('test', csrf_exempt(PushView.as_view())),

    path('events', csrf_exempt(EventListView.as_view())),
    path('events/<int:pk>', csrf_exempt(EventDetailView.as_view())),

    path('invitations', csrf_exempt(SendInviteView.as_view())),
    path('invitations/<int:pk>/responses', csrf_exempt(RespondInviteView.as_view())),
]