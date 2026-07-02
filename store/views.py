from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import datetime
import zoneinfo
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

def _fmt_time(dt):
    h = dt.hour % 12 or 12
    m = dt.strftime('%M')
    ap = 'AM' if dt.hour < 12 else 'PM'
    return f"{h}:{m} {ap}"

def _make_slots(now_local, asap_delta, hours_ahead, label_asap):
    asap = now_local + asap_delta
    slots = [{'value': asap.isoformat(), 'label': f"{label_asap} — {_fmt_time(asap)}"}]
    next_hour = asap.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    end_time = now_local + datetime.timedelta(hours=hours_ahead)
    cur = next_hour
    while cur <= end_time:
        slots.append({'value': cur.isoformat(), 'label': _fmt_time(cur)})
        cur += datetime.timedelta(hours=1)
    return slots

@login_required
def checkout(request):
    lang = get_lang(request)
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        return redirect('cart')

    tz_mx = zoneinfo.ZoneInfo('America/Mexico_City')
    now_local = timezone.now().astimezone(tz_mx)

    if lang == 'en':
        delivery_slots = _make_slots(now_local, datetime.timedelta(hours=1), 8, 'ASAP (~1 hour)')
        pickup_slots = _make_slots(now_local, datetime.timedelta(minutes=30), 6, 'ASAP (~30 min)')
    else:
        delivery_slots = _make_slots(now_local, datetime.timedelta(hours=1), 8, 'Lo antes posible (~1 hora)')
        pickup_slots = _make_slots(now_local, datetime.timedelta(minutes=30), 6, 'Lo antes posible (~30 min)')

    return render(request, 'store/checkout.html', {
        'cart': cart_obj,
        'lang': lang,
        'delivery_slots': delivery_slots,
        'pickup_slots': pickup_slots,
    })

@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        return redirect('cart')

    fulfillment_type = request.POST.get('fulfillment_type', 'delivery')
    delivery_address = request.POST.get('delivery_address', '')
    delivery_phone = request.POST.get('delivery_phone', '')
    business_name = request.POST.get('business_name', '')
    pickup_name = request.POST.get('pickup_name', '')
    pickup_phone = request.POST.get('pickup_phone', '')
    scheduled_time_str = request.POST.get('scheduled_time', '')

    scheduled_time = None
    if scheduled_time_str:
        try:
            scheduled_time = datetime.datetime.fromisoformat(scheduled_time_str)
        except ValueError:
            pass

    order = Order.objects.create(
        user=request.user,
        total_amount=cart_obj.get_total(),
        payment_id='CASH',
        payment_status='cash_on_delivery',
        fulfillment_type=fulfillment_type,
        delivery_address=delivery_address,
        delivery_phone=delivery_phone,
        business_name=business_name,
        pickup_name=pickup_name,
        pickup_phone=pickup_phone,
        scheduled_time=scheduled_time,
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

ACTIVE_STATUSES = ['pending', 'confirmed', 'preparing', 'ready']
COMPLETED_STATUSES = ['delivered', 'cancelled']

@login_required
def order_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    tz_mx = zoneinfo.ZoneInfo('America/Mexico_City')
    now_mx = timezone.now().astimezone(tz_mx)
    active_orders = Order.objects.filter(status__in=ACTIVE_STATUSES).order_by('-created_at').prefetch_related('items__product')
    completed_orders = Order.objects.filter(status__in=COMPLETED_STATUSES).order_by('-created_at').prefetch_related('items__product')[:20]
    return render(request, 'store/dashboard.html', {
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'now_mx': now_mx,
    })

@login_required
@require_POST
def update_order_status(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)
    order_id = request.POST.get('order_id')
    new_status = request.POST.get('status')
    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    order = get_object_or_404(Order, id=order_id)
    order.status = new_status
    order.save()
    return JsonResponse({'success': True})
