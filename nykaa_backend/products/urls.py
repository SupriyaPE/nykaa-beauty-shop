from django.urls import path
from .views import category_products,brand_products

urlpatterns = [
    path("category/<slug:slug>/", category_products, name="category_products"),
    path("brand/<slug:slug>/", brand_products, name="brand_products"),
]


