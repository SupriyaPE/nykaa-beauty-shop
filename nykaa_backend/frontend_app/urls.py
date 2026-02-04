from django.urls import path
from . import views
from .views import login_page,orders_page,order_success

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "category/<slug:slug>/",
        views.product_list,
        {"type": "category"},
        name="category_products"
    ),

    path(
        "brand/<slug:slug>/",
        views.product_list,
        {"type": "brand"},
        name="brand_products"
    ),

    path(
        "product/<slug:slug>/",
        views.product_detail,
        name="product_detail"
    ),

    path(
    "products/",
    views.product_list,
    name="all_products"
    ),


    # CHECKOUT PAGES (NO LOGIC)
    path("checkout/account/", views.checkout_account),
    path("checkout/address/", views.checkout_address),
    path("checkout/payment/", views.checkout_payment),    


    path("accounts/login/", login_page, name="login_page"),

    path("orders/", views.orders_page),

    path("orders/profile/", views.profile_page, name="account-profile"),
    path("orders/orders/", views.orders_page, name="account-orders"),
    path("orders/wishlist/", views.wishlist_page, name="account-wishlist"),
    path("orders/success/", views.order_success, name="order_success"),

]
