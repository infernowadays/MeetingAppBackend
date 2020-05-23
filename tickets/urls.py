from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('tickets/', TicketListView.as_view()),
    path('tickets/<int:pk>', csrf_exempt(TicketDetailView.as_view())),
]
