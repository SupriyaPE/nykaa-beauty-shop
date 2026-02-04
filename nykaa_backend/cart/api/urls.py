from django.urls import path
from .views import view_cart, add_to_cart, update_quantity, remove_item

urlpatterns = [
    path('', view_cart),
    path('add/', add_to_cart),
    path('update/', update_quantity),
    path('remove/', remove_item),
]
