from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('events/', csrf_exempt(EventListView.as_view())),
    path('events/<int:pk>/', csrf_exempt(EventDetailView.as_view())),

    path('events/<int:pk>/members/<int:uid>/', csrf_exempt(EventMembersView.as_view())),

    path('requests/', csrf_exempt(RequestListView.as_view())),
    path('requests/<int:pk>/', csrf_exempt(RespondRequestView.as_view())),
]
