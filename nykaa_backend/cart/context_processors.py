from cart.models import Cart


def bag_count(request):
  
    cart = None
    count = 0

    # AUTHENTICATED USER
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

    # GUEST USER
    else:
        guest_id = request.COOKIES.get("guest_id")
        if guest_id:
            cart = Cart.objects.filter(guest_id=guest_id).first()

    if cart:
        count = cart.items.count()

    return {"bag_count": count}
