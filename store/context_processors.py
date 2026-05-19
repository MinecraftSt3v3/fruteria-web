from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return {'cart_count': int(cart.get_item_count())}
    return {'cart_count': 0}

def language_context(request):
    return {'lang': request.session.get('lang', 'es')}
