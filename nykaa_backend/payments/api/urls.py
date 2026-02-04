from django.urls import path
from .views import create_razorpay_order, verify_razorpay_payment

urlpatterns = [
    path("create-order/", create_razorpay_order),
    path("verify/", verify_razorpay_payment),
]
