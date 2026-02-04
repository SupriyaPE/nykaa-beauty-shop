from django.shortcuts import render, get_object_or_404, redirect
from products.models import (
    Category,
    Brand,
    Product,
    ProductVariant,
    ProductImage,
    Banner,
)

# =========================
# HOME PAGE
# =========================
def home(request):
    hero_banners = Banner.objects.filter(
        banner_type="hero",
        is_active=True
    ).order_by("position")

    offer_banner = Banner.objects.filter(
        banner_type="offer",
        is_active=True
    ).order_by("position").first()

    strip_banner = Banner.objects.filter(
        banner_type="strip",
        is_active=True
    ).order_by("position").first()

    brands = Brand.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    # 🔥 Attach redirect_url dynamically (NO DB CHANGE)
    def attach_redirect(banner):
        title = banner.title.lower()

        for brand in brands:
            if brand.name.lower() in title:
                banner.redirect_url = f"/brand/{brand.slug}/"
                return banner

        for cat in categories:
            if cat.name.lower() in title:
                banner.redirect_url = f"/category/{cat.slug}/"
                return banner

        banner.redirect_url = "/products/"
        return banner

    hero_banners = [attach_redirect(b) for b in hero_banners]

    if offer_banner:
        offer_banner = attach_redirect(offer_banner)

    if strip_banner:
        strip_banner = attach_redirect(strip_banner)

    top_categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).order_by("header_order")[:6]

    featured_products = Product.objects.filter(
        is_featured=True,
        is_active=True
    ).prefetch_related("variants__images", "brand")

    return render(request, "home.html", {
        "hero_banners": hero_banners,
        "offer_banner": offer_banner,
        "strip_banner": strip_banner,
        "brands": brands[:12],
        "top_categories": top_categories,
        "featured_products": featured_products,
    })


# =========================
# PRODUCT LIST (WITH FILTERS)
# =========================
from django.db.models import Q

def product_list(request, slug=None, type=None):
    products = Product.objects.filter(is_active=True).prefetch_related(
        "variants__images",
        "brand",
        "category"
    )

    current_filter = "All Products"

    # =====================
    # SEARCH (NEW)
    # =====================
    search_query = request.GET.get("q")
    if search_query:
        current_filter = f"Search results for '{search_query}'"
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # =====================
    # CATEGORY PAGE
    # =====================
    if type == "category":
        category = get_object_or_404(Category, slug=slug, is_active=True)
        current_filter = category.name

        category_ids = [category.id]

        children = category.children.filter(is_active=True)
        category_ids += list(children.values_list("id", flat=True))

        grandchildren = Category.objects.filter(
            parent__in=children,
            is_active=True
        )
        category_ids += list(grandchildren.values_list("id", flat=True))

        products = products.filter(category_id__in=category_ids)

    # =====================
    # BRAND PAGE
    # =====================
    if type == "brand":
        brand = get_object_or_404(Brand, slug=slug, is_active=True)
        current_filter = brand.name
        products = products.filter(brand=brand)

    # ================= FILTERS =================
    brand_filter = request.GET.get("brand")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if brand_filter:
        products = products.filter(brand__slug=brand_filter)

    if min_price:
        products = products.filter(variants__selling_price__gte=min_price)

    if max_price:
        products = products.filter(variants__selling_price__lte=max_price)

    products = products.distinct()

    return render(request, "products/product_list.html", {
        "products": products,
        "brands": Brand.objects.filter(is_active=True),
        "current_filter": current_filter
    })

# =========================
# PRODUCT DETAIL
# =========================
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("variants__images", "brand"),
        slug=slug,
        is_active=True
    )

    variants = product.variants.filter(is_active=True)
    selected_variant = variants.first()

    images = []
    primary_image = None

    if selected_variant:
        images = selected_variant.images.all()
        primary_image = images.filter(is_primary=True).first() or images.first()

    return render(request, "products/product_detail.html", {
        "product": product,
        "variants": variants,
        "selected_variant": selected_variant,
        "images": images,
        "primary_image": primary_image,
    })





def checkout_account(request):
    return render(request, "checkout/checkout_account.html")

def checkout_address(request):
    return render(request, "checkout/checkout_address.html")

def checkout_payment(request):
    return render(request, "checkout/checkout_payment.html")



def login_page(request):
    return render(request, "accounts/login.html")    




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect("/")
    return render(request, "orders/profile.html")

def orders_page(request):
    if not request.user.is_authenticated:
        return redirect("/")
    return render(request, "orders/orders.html")

def wishlist_page(request):
    if not request.user.is_authenticated:
        return redirect("/")
    return render(request, "orders/wishlist.html")      


from django.shortcuts import render
from orders.models import Order

def order_success(request):
    order_id = request.GET.get("order_id")

    if not order_id:
        return render(request, "orders/success.html")

    order = Order.objects.filter(id=order_id).first()

    return render(request, "orders/success.html", {
        "order": order
    })