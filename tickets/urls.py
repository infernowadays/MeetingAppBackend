from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('tickets', csrf_exempt(TicketsView.as_view())),
]
