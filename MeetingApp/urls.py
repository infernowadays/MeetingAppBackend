from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('token_auth/', include('token_auth.urls')),
    path('api/', include('events.urls')),
    path('tickets/', include('tickets.urls')),
    path('chat/', include('chat.urls')),
]
