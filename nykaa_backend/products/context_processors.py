from django.db.models import Q
from .models import Category, Brand


def header_categories(request):
    # 🔹 Main Categories (normal header: Categories menu)
    header_categories = (
        Category.objects
        .filter(
            parent__isnull=True,
            is_active=True,
            show_in_header=True
        )
        .prefetch_related("children")
        .order_by("header_order")
    )

    # 🔹 Header Brands (logos only – does NOT affect home page)
    header_brands = (
        Brand.objects
        .filter(
            is_active=True,
            header_logo__isnull=False
        )
        .order_by("name")
    )

    # 🔹 Luxe Categories (ONLY parent + direct children)
    luxe_categories = (
        Category.objects
        .filter(
            parent__isnull=True,
            is_active=True,
            is_luxe=True
        )
        .prefetch_related("children")
        .order_by("header_order")
    )

    # 🔹 Nykaa Fashion
    # 👉 Select ONLY sub-categories in admin
    # 👉 Auto include their child categories
    # 🔹 Nykaa Fashion (STRICT CONTROL)


    fashion_categories = (
        Category.objects
        .filter(
            is_active=True,
            parent__isnull=False,              # 🚫 removes main categories
        )
        .filter(
            Q(show_in_fashion_header=True) |   # selected sub-category
            Q(parent__show_in_fashion_header=True)  # its children
        )
        .select_related("parent")
        .order_by("header_order", "name")
    )

    return {
        "header_categories": header_categories,
        "header_brands": header_brands,
        "luxe_categories": luxe_categories,
        "fashion_categories": fashion_categories,
    }