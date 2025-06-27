from django.db import models
from django.conf import settings
from courses.models import Course, Enrollment
import uuid


class Certificate(models.Model):
    """Certificate model for course completion"""

    # Unique certificate identifier
    certificate_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    # Related models
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='certificate'
    )

    # Certificate details
    issued_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField()
    final_score = models.PositiveIntegerField(
        help_text="Final course score percentage"
    )

    # PDF file
    pdf_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True
    )

    # Verification
    is_verified = models.BooleanField(default=True)
    verification_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-issued_date']

    def __str__(self):
        return f"Certificate for {self.student.get_full_name()} - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)

    def generate_verification_code(self):
        """Generate a unique verification code"""
        import random
        import string

        while True:
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits,
                k=10
            ))
            if not Certificate.objects.filter(verification_code=code).exists():
                return code

    @property
    def certificate_url(self):
        """Get the URL for certificate verification"""
        from django.urls import reverse
        return reverse('certificates:verify_certificate', kwargs={
            'certificate_id': self.certificate_id
        })


class CertificateTemplate(models.Model):
    """Template for certificate design"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Template settings
    background_color = models.CharField(
        max_length=7,
        default='#FFFFFF',
        help_text="Hex color code"
    )
    text_color = models.CharField(
        max_length=7,
        default='#000000',
        help_text="Hex color code"
    )
    border_color = models.CharField(
        max_length=7,
        default='#000000',
        help_text="Hex color code"
    )

    # Logo and images
    logo = models.ImageField(
        upload_to='certificate_templates/',
        blank=True,
        null=True
    )
    background_image = models.ImageField(
        upload_to='certificate_templates/',
        blank=True,
        null=True
    )

    # Text settings
    title_font_size = models.PositiveIntegerField(default=24)
    body_font_size = models.PositiveIntegerField(default=12)

    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one default template
        if self.is_default:
            CertificateTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
