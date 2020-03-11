from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import *


urlpatterns = [
    path('test', csrf_exempt(PushView.as_view())),

    path('events', csrf_exempt(EventsView.as_view())),
    path('events/<int:event_id>', csrf_exempt(GetEventInfoView.as_view())),

    path('invitations', csrf_exempt(InviteUsersView.as_view())),
    path('invitations/<int:invitation_id>', csrf_exempt(GetInvitationView.as_view())),
    path('invitations/<int:invitation_id>/responses', csrf_exempt(RespondInvitationView.as_view())),
]