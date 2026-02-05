from django.urls import path
from .views import send_otp, verify_otp, complete_signup, logout,profile_view

urlpatterns = [
    path("send-otp/", send_otp),
    path("verify-otp/", verify_otp),
    path("complete-signup/", complete_signup),
    path("logout/", logout),
    path("profile/", profile_view),
]