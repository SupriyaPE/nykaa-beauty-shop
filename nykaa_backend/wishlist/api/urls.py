from django.urls import path
from .views import toggle_wishlist, wishlist_list,wishlist_ids

urlpatterns = [
    path("toggle/", toggle_wishlist),
    path("", wishlist_list),
    path("ids/", wishlist_ids),   # ✅ ADD THIS
]