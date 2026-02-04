from django.urls import path
from .views import address_list_create

urlpatterns = [
    path("", address_list_create),
]