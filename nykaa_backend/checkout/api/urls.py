# checkout/api/urls.py

from django.urls import path
from .views import checkout_account_status,save_guest_address

urlpatterns = [
    path("account-status/", checkout_account_status),
    path("guest-address/", save_guest_address),
]