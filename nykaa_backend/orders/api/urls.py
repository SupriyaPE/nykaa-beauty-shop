from django.urls import path
from .views import create_order,my_orders,get_order_summary

urlpatterns = [
    path("create/", create_order),
    path("my-orders/", my_orders),
    path("order-summary/<int:order_id>/", get_order_summary),
]