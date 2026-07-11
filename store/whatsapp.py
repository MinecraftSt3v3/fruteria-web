import logging

from twilio.rest import Client
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp(to_number, message):
    """Send a WhatsApp message via Twilio. Logs and returns without raising if it can't be sent."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.error("WhatsApp send skipped: TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN not configured")
        return
    if not to_number:
        logger.error("WhatsApp send skipped: no destination phone number provided")
        return
    # Normalize phone number - ensure it has country code
    phone = to_number.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if not phone.startswith('+'):
        phone = '+52' + phone  # default to Mexico country code
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        result = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=f'whatsapp:{phone}',
            body=message
        )
        logger.info("WhatsApp message queued: sid=%s to=%s status=%s", result.sid, phone, result.status)
    except Exception:
        logger.error("WhatsApp send error: to=%s from=%s", phone, settings.TWILIO_WHATSAPP_FROM, exc_info=True)


def notify_order_confirmed(order):
    """Send order confirmation with full receipt."""
    phone = order.delivery_phone or order.pickup_phone
    if not phone:
        return

    items_es = '\n'.join([f"  • {item.product_name_es} x{item.quantity} {item.unit} — ${item.price * item.quantity:.1f}" for item in order.items.all()])
    items_en = '\n'.join([f"  • {item.product_name_en} x{item.quantity} {item.unit} — ${item.price * item.quantity:.1f}" for item in order.items.all()])

    if order.fulfillment_type == 'delivery':
        fulfillment_es = f"🚚 Entrega a: {order.delivery_address}"
        fulfillment_en = f"🚚 Delivery to: {order.delivery_address}"
    else:
        fulfillment_es = f"🏪 Recoge en tienda"
        fulfillment_en = f"🏪 Pick up in store"

    scheduled = order.scheduled_time.strftime('%I:%M %p') if order.scheduled_time else 'Por confirmar'

    message = f"""✅ *Pedido Confirmado — Frutería Elí*

📋 Pedido: {order.order_number}
{fulfillment_es}
🕐 Hora estimada: {scheduled}

*Tus productos:*
{items_es}

💵 Total: ${order.total_amount:.1f} (Pago en efectivo)

¡Gracias por tu pedido! Te avisaremos cuando esté listo.

---
✅ *Order Confirmed — Frutería Elí*
📋 Order: {order.order_number}
{fulfillment_en}
🕐 Estimated time: {scheduled}
💵 Total: ${order.total_amount:.1f} (Cash payment)"""

    send_whatsapp(phone, message)


def notify_order_status_update(order):
    """Send status update when order moves through the pipeline."""
    phone = order.delivery_phone or order.pickup_phone
    if not phone:
        return

    status_messages = {
        'confirmed': (
            f"👍 *Frutería Elí* — Pedido {order.order_number} confirmado. ¡Estamos en ello!\n"
            f"Order {order.order_number} confirmed. We're on it!"
        ),
        'preparing': (
            f"🧺 *Frutería Elí* — Estamos preparando tu pedido {order.order_number} ahora mismo.\n"
            f"We're now preparing your order {order.order_number}."
        ),
        'ready': (
            f"✅ *Frutería Elí* — Tu pedido {order.order_number} está LISTO.\n"
            f"{'🚚 El repartidor va en camino.' if order.fulfillment_type == 'delivery' else '🏪 Puedes pasar a recogerlo.'}\n\n"
            f"Your order {order.order_number} is READY.\n"
            f"{'🚚 The driver is on their way.' if order.fulfillment_type == 'delivery' else '🏪 You can come pick it up.'}"
        ),
        'delivered': (
            f"🎉 *Frutería Elí* — ¡Tu pedido {order.order_number} fue entregado! Gracias por tu compra. 🍓\n"
            f"Your order {order.order_number} has been delivered! Thank you for your purchase. 🍓"
        ),
    }

    message = status_messages.get(order.status)
    if message:
        send_whatsapp(phone, message)
