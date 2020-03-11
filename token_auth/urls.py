from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from token_auth import views


urlpatterns = [
    path('auth', csrf_exempt(views.LoginView.as_view())),
    path('users', csrf_exempt(views.SignUpView.as_view())),
]