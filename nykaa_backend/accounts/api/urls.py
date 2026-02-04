from django.urls import path
from .views import login,signup_view,send_otp,verify_otp,logout


urlpatterns = [
    path("login/", login),
    path("signup/", signup_view),
    path("send-otp/", send_otp),
    path("verify-otp/",verify_otp),
    path("logout/",logout),
]
