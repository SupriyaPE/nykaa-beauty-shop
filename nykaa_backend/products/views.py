from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    return render(request, "products/category_products.html", {
        "category": category,
        "products": products
    })



def brand_products(request, slug):
    brand = get_object_or_404(Brand, slug=slug, is_active=True)

    products = Product.objects.filter(
        brand=brand,
        is_active=True
    ).select_related("brand", "category").prefetch_related("variants")

    return render(request, "products/brand_products.html", {
        "brand": brand,
        "products": products
    })