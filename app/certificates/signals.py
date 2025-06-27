from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Enrollment
from .utils import generate_certificate_for_enrollment


@receiver(post_save, sender=Enrollment)
def auto_generate_certificate(sender, instance, created, **kwargs):
    """Automatically generate certificate when course is completed"""
    if not created and instance.progress_percentage == 100 and instance.completed_at:
        # Check if certificate doesn't already exist
        if not hasattr(instance, 'certificate'):
            try:
                generate_certificate_for_enrollment(instance)
            except Exception as e:
                # Log the error but don't raise it to avoid breaking the enrollment save
                print(f"Failed to generate certificate for enrollment {instance.id}: {str(e)}")
