from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('token_auth/', include('token_auth.urls')),
    path('api/', include('events.urls')),
    path('api/', include('tickets.urls')),
    path('api/', include('chat.urls')),
    path('api/', include('common.urls')),
    path('api/', include('email_service.urls')),
    path('api/', include('moderator.urls')),
]
