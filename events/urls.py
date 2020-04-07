from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import *


urlpatterns = [
    path('test', csrf_exempt(PushView.as_view())),

    path('events', csrf_exempt(EventListView.as_view())),
    path('events/<int:pk>', csrf_exempt(EventDetailView.as_view())),

    path('requests', csrf_exempt(SendRequestView.as_view())),
    path('requests/<int:pk>/responses', csrf_exempt(ReceiveRequestView.as_view())),
]