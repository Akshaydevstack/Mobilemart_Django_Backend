from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import threading
import time
from .models import Order, OrderItem, ShippingInfo
from products.models import ProductImage


@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    if not created:
        return

    # Use transaction.on_commit to ensure OrderItems are created
    transaction.on_commit(lambda: _send_order_email(instance))


def _send_order_email(order_instance):
    """Helper function to send order email after transaction commit"""
    
    user = order_instance.user
    order_items = OrderItem.objects.filter(order=order_instance)
    
    # Try to get shipping info if it exists
    shipping_info = None
    try:
        shipping_info = ShippingInfo.objects.get(order=order_instance)
    except ShippingInfo.DoesNotExist:
        pass

    print(f"📦 Order #{order_instance.id} has {order_items.count()} items")
    
    if order_items.count() == 0:
        print(f"⚠️ No items found for order #{order_instance.id}. Retrying in 2 seconds...")
        # Retry after a short delay to ensure items are created
        def retry_send_email():
            time.sleep(2)
            order_items_retry = OrderItem.objects.filter(order=order_instance)
            print(f"🔄 Retry - Order #{order_instance.id} has {order_items_retry.count()} items")
            if order_items_retry.count() > 0:
                _send_order_email_final(order_instance, order_items_retry, shipping_info)
            else:
                print(f"❌ Still no items found for order #{order_instance.id}")
        
        threading.Thread(target=retry_send_email).start()
        return
    
    _send_order_email_final(order_instance, order_items, shipping_info)





def _send_order_email_final(order_instance, order_items, shipping_info):
    """Final function to send the email"""
    
    # Build order summary for email with product images
    items = []
    for item in order_items:
        # Get product images - get the first image for this product
        product_images = ProductImage.objects.filter(product=item.product)
        product_image = None
        is_image_url = False
        placeholder = _get_product_placeholder(item.product)
        
        if product_images.exists():
            # Use the first product image
            product_image = product_images.first().image_url
            # Check if it's a valid URL (simple check)
            is_image_url = product_image and (
                product_image.startswith('http://') or 
                product_image.startswith('https://') or
                product_image.startswith('/')
            )
        else:
            # Use placeholder emoji
            product_image = placeholder
            is_image_url = False
        
        # Get brand name for additional info
        brand_name = getattr(item.product.brand, 'name', 'Unknown Brand')
        
        items.append({
            "name": item.product.name,
            "brand": brand_name,
            "quantity": item.quantity,
            "price": float(item.price),
            "total": float(item.quantity * item.price),
            "image": product_image,
            "is_image_url": is_image_url,
            "placeholder": placeholder,
            "description": getattr(item.product, 'description', '')[:100] + '...' if getattr(item.product, 'description', '') else '',
        })

    subject = f"🎉 Order Confirmed! Order #{order_instance.id} - Thank You!"

    context = {
        "user": order_instance.user,
        "order": order_instance,
        "items": items,
        "shipping_info": shipping_info,
        "current_year": timezone.now().year,
    }

    html_content = render_to_string("emails/order_confirmation.html", context)
    text_content = render_to_string("emails/order_confirmation.txt", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order_instance.user.email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        print(f"✅ Order confirmation email sent for order #{order_instance.id}")
    except Exception as e:
        print(f"❌ Failed to send email for order #{order_instance.id}: {str(e)}")




def _get_product_placeholder(product):
    """Get a placeholder emoji based on product name or category"""
    product_name_lower = product.name.lower()
    
    if any(word in product_name_lower for word in ['phone', 'mobile', 'smartphone']):
        return "📱"
   