from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('categories', csrf_exempt(CategoryListView.as_view())),
]
