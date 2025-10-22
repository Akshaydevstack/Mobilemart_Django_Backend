# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import User
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.hashers import check_password


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = "Welcome to MobileMart! 🎉"
        
        # Context for the template
        context = {
            'username': instance.username,
            'current_year': timezone.now().year,
        }
        
        # Render HTML and text content
        html_content = render_to_string('emails/welcome.html', context)
        text_content = f"""
Welcome to MobileMart, {instance.username}!

Thank you for registering at MobileMart! We're excited to have you onboard.

Explore the latest mobile technology with:
• Latest smartphones and accessories
• Fast and secure delivery
• 24/7 customer support

Get started: http://localhost:5173

Need help? Contact us at support@mobilemart.com

— The MobileMart Team
        """
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        try:
            email.send(fail_silently=False)
            print(f"✅ Welcome email sent to {instance.email}")
        except Exception as e:
            print(f"❌ Failed to send welcome email: {str(e)}")




@receiver(pre_save, sender=User)
def cache_old_user_data(sender, instance, **kwargs):
    """Cache old email and password before saving (for comparison)."""
    if instance.pk:  # only for existing users
        try:
            old_user = User.objects.get(pk=instance.pk)
            instance._old_email = old_user.email
            instance._old_password = old_user.password
        except User.DoesNotExist:
            instance._old_email = None
            instance._old_password = None
    else:
        instance._old_email = None
        instance._old_password = None


# ✉️ Step 2: Detect changes and send notifications
@receiver(post_save, sender=User)
def notify_user_changes(sender, instance, created, **kwargs):
    """Send email notification if user email or password changes."""
    if created:
        # Skip new user creation (handled by welcome email)
        return

    old_email = getattr(instance, "_old_email", None)
    old_password = getattr(instance, "_old_password", None)

    # 📨 Email change detection
    if old_email and old_email != instance.email:
        subject = "Your MobileMart account email has been updated ✉️"
        context = {
            "username": instance.username or instance.email,
            "old_email": old_email,
            "new_email": instance.email,
            "date": timezone.now().strftime("%B %d, %Y at %I:%M %p"),
        }

        html_content = render_to_string("emails/email_changed.html", context)
        text_content = f"""
Hi {context['username']},

We wanted to let you know that your email address for your MobileMart account
has been changed from {old_email} to {instance.email}.

If this wasn’t you, please contact support immediately at support@mobilemart.com.

— The MobileMart Security Team
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.email],
        )
        email.attach_alternative(html_content, "text/html")
        try:
            email.send(fail_silently=False)
            print(f"📧 Email change notification sent to {instance.email}")
        except Exception as e:
            print(f"❌ Failed to send email change notification: {e}")

    # 🔐 Password change detection
    elif old_password and not check_password(instance.password, old_password):
        subject = "Your MobileMart password has been changed 🔒"
        context = {
            "username": instance.username or instance.email,
            "date": timezone.now().strftime("%B %d, %Y at %I:%M %p"),
        }

        html_content = render_to_string("emails/password_changed.html", context)
        text_content = f"""
Hi {context['username']},

Your MobileMart account password was recently changed.

If you did not make this change, please reset your password immediately or contact support.

— The MobileMart Security Team
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.email],
        )
        email.attach_alternative(html_content, "text/html")
        try:
            email.send(fail_silently=False)
            print(f"🔐 Password change notification sent to {instance.email}")
        except Exception as e:
            print(f"❌ Failed to send password change notification: {e}")