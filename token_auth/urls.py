from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from token_auth import views

urlpatterns = [
    path('auth/', csrf_exempt(views.LoginView.as_view())),
    path('users/', csrf_exempt(views.SignUpView.as_view())),
    path('password/', csrf_exempt(views.ChangePasswordView.as_view())),

    path('profile/<int:pk>/', csrf_exempt(views.ProfileView.as_view())),
    path('profile/me/', csrf_exempt(views.MyProfileView.as_view())),
    path('profile/upload/', csrf_exempt(views.UploadPhotoView.as_view())),
    path('tokens/', csrf_exempt(views.FirebaseTokenView.as_view())),
]
