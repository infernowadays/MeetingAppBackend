from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('check_code/', csrf_exempt(views.CheckConfirmationCodeView.as_view())),
    path('generate_code/', csrf_exempt(views.GenerateConfirmationView.as_view())),
]
