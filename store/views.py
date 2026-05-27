from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
import json
import stripe
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Category, Cart, CartItem, Order, OrderItem

def get_lang(request):
    return request.session.get('lang', 'es')

def set_language(request):
    lang = request.GET.get('lang', 'es')
    if lang not in ('es', 'en'):
        lang = 'es'
    request.session['lang'] = lang
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    if not next_url.startswith('/'):
        next_url = '/'
    return redirect(next_url)

def home(request):
    lang = get_lang(request)
    featured = Product.objects.filter(is_available=True, is_special=True)[:6]
    products = Product.objects.filter(is_available=True)[:8]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'featured': featured,
        'products': products,
        'categories': categories,
        'lang': lang,
    })

def about(request):
    lang = get_lang(request)
    return render(request, 'store/about.html', {'lang': lang})

def shop(request):
    lang = get_lang(request)
    category_slug = request.GET.get('category')
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    active_cat = None
    if category_slug:
        active_cat = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_cat)
    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories,
        'active_cat': active_cat,
        'lang': lang,
    })

@login_required
def cart(request):
    lang = get_lang(request)
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart_obj, 'lang': lang})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product)
    if not created:
        item.quantity += 1
        item.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': int(cart_obj.get_item_count())})
    messages.success(request, f"{'Agregado al carrito' if get_lang(request) == 'es' else 'Added to cart'}!")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    qty = request.POST.get('quantity', 1)
    try:
        qty = float(qty)
        if qty <= 0:
            item.delete()
        else:
            item.quantity = qty
            item.save()
    except ValueError:
        pass
    return redirect('cart')

@login_required
def checkout(request):
    lang = get_lang(request)
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        return redirect('cart')
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    return render(request, 'store/checkout.html', {
        'cart': cart_obj,
        'lang': lang,
        'stripe_public_key': stripe_public_key,
    })

@login_required
def create_payment_intent(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        return JsonResponse({'error': 'cart empty'}, status=400)
    # amount in cents
    amount = int(cart_obj.get_total() * 100)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='mxn',
        metadata={'user_id': request.user.id}
    )
    return JsonResponse({'client_secret': intent.client_secret, 'payment_intent_id': intent.id})

@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        return redirect('cart')

    payment_id = request.POST.get('payment_id', '')
    payment_method = request.POST.get('payment_method', 'card')
    notes = request.POST.get('notes', '')

    if payment_method == 'cash':
        payment_id = 'CASH'
        payment_status = 'cash_on_delivery'
    else:
        payment_status = 'approved' if payment_id else 'pending'

    order = Order.objects.create(
        user=request.user,
        total_amount=cart_obj.get_total(),
        payment_id=payment_id,
        payment_status=payment_status,
        notes=notes,
    )
    for item in cart_obj.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name_es=item.product.name_es,
            product_name_en=item.product.name_en,
            quantity=item.quantity,
            unit=item.product.unit,
            price=item.product.price,
        )
    cart_obj.items.all().delete()
    return redirect('order_receipt', order_id=order.id)

@login_required
def order_receipt(request, order_id):
    lang = get_lang(request)
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/receipt.html', {'order': order, 'lang': lang})

@login_required
def my_orders(request):
    lang = get_lang(request)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders, 'lang': lang})
