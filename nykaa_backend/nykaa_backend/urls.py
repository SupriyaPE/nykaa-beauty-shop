"""
URL configuration for nykaa_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend_app.urls')),
    path('api/', include('products.api.urls')),
    path('api/cart/', include('cart.api.urls')),
    path('api/auth/', include('accounts.api.urls')),
    path("api/checkout/", include("checkout.api.urls")), 
    path("api/addresses/", include("addresses.api.urls")),
    path("api/orders/", include("orders.api.urls")),
    path("api/payment/", include("payments.api.urls")),
    path("api/wishlist/", include("wishlist.api.urls")),
]




urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]