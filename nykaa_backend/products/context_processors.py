from .models import Category, Brand

def header_categories(request):
    header_categories = (
        Category.objects
        .filter(
            parent__isnull=True,
            is_active=True,
            show_in_header=True
        )
        .prefetch_related("children__children")
        .order_by("header_order")
    )

    # ✅ Header dropdown brands (logos only)
    header_brands = Brand.objects.filter(
        is_active=True,
        header_logo__isnull=False
    ).order_by("name")

    # ✅ Home page brands (cards / images – existing behavior stays)
    home_brands = Brand.objects.filter(
        is_active=True
    ).order_by("name")

    return {
        "header_categories": header_categories,
        "header_brands": header_brands,
        "home_brands": home_brands,
    }