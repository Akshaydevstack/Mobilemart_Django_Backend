from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from products.models import Product
from .models import ProductNotificationSubscription, Notification  # ✅ added Notification
from .utils import send_notification_to_user
from users.models import User


@receiver(pre_save, sender=Product)
def detect_upcoming_to_available(sender, instance, **kwargs):
    if not instance.pk:
        instance._became_available = False
        return

    try:
        previous = Product.objects.get(pk=instance.pk)
        instance._became_available = previous.upcoming and not instance.upcoming
    except Product.DoesNotExist:
        instance._became_available = False


@receiver(post_save, sender=Product)
def notify_users_when_available(sender, instance, created, **kwargs):
    if getattr(instance, "_became_available", False):
        subscribers = ProductNotificationSubscription.objects.filter(
            product=instance, notified=False
        )

        for sub in subscribers:
            message = f"🎉 {instance.name} is now available! Check it out on MobileMart."
            send_notification_to_user(sub.user.id, message)

            user = User.objects.get(id=sub.user.id)
            user_email = user.email

            # ✅ Save notification to database
            Notification.objects.create(
                user=sub.user,
                title=f"{instance.name} Now Available 🎉",
                message=message,
            )

            # ✅ Keep your existing email logic
            subject = f"{instance.name} is now available!"
            context = {
                "username": sub.user.username or sub.user.email,
                "product_name": instance.name,
                "product_price": instance.price,
                "product_link": f"http://localhost:5173/product/{instance.id}",  # change to your actual frontend link
                "site_name": "MobileMart",
            }

            html_content = render_to_string("emails/product_available.html", context)
            text_content = (
                f"Hello {context['username']},\n\n"
                f"{instance.name} is now available on MobileMart! 🎉\n"
                f"Check it out here: {context['product_link']}\n\n"
                f"Thanks,\nThe MobileMart Team"
            )

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            sub.notified = True
            sub.save()
    else:
        print(f"[DEBUG] No availability change for {instance.name}")