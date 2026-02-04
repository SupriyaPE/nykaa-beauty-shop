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

    header_brands = Brand.objects.filter(is_active=True)

    return {
        "header_categories": header_categories,
        "header_brands": header_brands
    }