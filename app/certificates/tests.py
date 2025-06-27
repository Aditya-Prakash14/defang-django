from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from django.utils import timezone
from courses.models import Course, Enrollment
from .models import Certificate, CertificateTemplate
from .utils import generate_certificate_for_enrollment, verify_certificate

User = get_user_model()


class CertificateModelTest(TestCase):
    """Test Certificate model"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            user_type='instructor'
        )

        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            user_type='student',
            first_name='John',
            last_name='Doe'
        )

        self.course = Course.objects.create(
            title='Python Basics',
            description='Learn Python programming',
            instructor=self.instructor,
            price=Decimal('0.00'),
            is_free=True,
            difficulty_level='beginner',
            duration_hours=10,
            is_published=True
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            is_active=True,
            progress_percentage=100,
            completed_at=timezone.now()
        )

    def test_create_certificate(self):
        """Test creating a certificate"""
        certificate = Certificate.objects.create(
            student=self.student,
            course=self.course,
            enrollment=self.enrollment,
            completion_date=self.enrollment.completed_at,
            final_score=95
        )

        self.assertEqual(certificate.student, self.student)
        self.assertEqual(certificate.course, self.course)
        self.assertEqual(certificate.enrollment, self.enrollment)
        self.assertEqual(certificate.final_score, 95)
        self.assertTrue(certificate.is_verified)
        self.assertIsNotNone(certificate.certificate_id)
        self.assertIsNotNone(certificate.verification_code)

    def test_certificate_str_representation(self):
        """Test certificate string representation"""
        certificate = Certificate.objects.create(
            student=self.student,
            course=self.course,
            enrollment=self.enrollment,
            completion_date=self.enrollment.completed_at,
            final_score=95
        )

        expected = f"Certificate for {self.student.get_full_name()} - {self.course.title}"
        self.assertEqual(str(certificate), expected)

    def test_verification_code_generation(self):
        """Test verification code is generated automatically"""
        certificate = Certificate.objects.create(
            student=self.student,
            course=self.course,
            enrollment=self.enrollment,
            completion_date=self.enrollment.completed_at,
            final_score=95
        )

        self.assertIsNotNone(certificate.verification_code)
        self.assertEqual(len(certificate.verification_code), 10)


class CertificateTemplateTest(TestCase):
    """Test Certificate Template model"""

    def test_create_template(self):
        """Test creating a certificate template"""
        template = CertificateTemplate.objects.create(
            name='Default Template',
            description='Default certificate template',
            background_color='#FFFFFF',
            text_color='#000000',
            border_color='#000000',
            is_default=True,
            is_active=True
        )

        self.assertEqual(template.name, 'Default Template')
        self.assertTrue(template.is_default)
        self.assertTrue(template.is_active)

    def test_only_one_default_template(self):
        """Test that only one template can be default"""
        # Create first default template
        template1 = CertificateTemplate.objects.create(
            name='Template 1',
            is_default=True,
            is_active=True
        )

        # Create second default template
        template2 = CertificateTemplate.objects.create(
            name='Template 2',
            is_default=True,
            is_active=True
        )

        # Refresh from database
        template1.refresh_from_db()

        # Only the second template should be default
        self.assertFalse(template1.is_default)
        self.assertTrue(template2.is_default)


class CertificateUtilsTest(TestCase):
    """Test certificate utility functions"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            user_type='instructor'
        )

        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            user_type='student',
            first_name='John',
            last_name='Doe'
        )

        self.course = Course.objects.create(
            title='Python Basics',
            description='Learn Python programming',
            instructor=self.instructor,
            price=Decimal('0.00'),
            is_free=True,
            difficulty_level='beginner',
            duration_hours=10,
            is_published=True
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            is_active=True,
            progress_percentage=100,
            completed_at=timezone.now()
        )

    def test_generate_certificate_for_enrollment(self):
        """Test generating certificate for enrollment"""
        certificate = generate_certificate_for_enrollment(self.enrollment)

        self.assertIsInstance(certificate, Certificate)
        self.assertEqual(certificate.student, self.student)
        self.assertEqual(certificate.course, self.course)
        self.assertEqual(certificate.enrollment, self.enrollment)
        self.assertTrue(certificate.is_verified)

    def test_verify_certificate_by_id(self):
        """Test certificate verification by ID"""
        certificate = Certificate.objects.create(
            student=self.student,
            course=self.course,
            enrollment=self.enrollment,
            completion_date=self.enrollment.completed_at,
            final_score=95
        )

        result = verify_certificate(certificate_id=certificate.certificate_id)

        self.assertTrue(result['valid'])
        self.assertEqual(result['certificate'], certificate)
        self.assertEqual(result['student_name'], 'John Doe')
        self.assertEqual(result['course_title'], 'Python Basics')

    def test_verify_certificate_by_code(self):
        """Test certificate verification by verification code"""
        certificate = Certificate.objects.create(
            student=self.student,
            course=self.course,
            enrollment=self.enrollment,
            completion_date=self.enrollment.completed_at,
            final_score=95
        )

        result = verify_certificate(verification_code=certificate.verification_code)

        self.assertTrue(result['valid'])
        self.assertEqual(result['certificate'], certificate)

    def test_verify_invalid_certificate(self):
        """Test verification of invalid certificate"""
        result = verify_certificate(certificate_id='invalid-id')

        self.assertFalse(result['valid'])
        self.assertIn('Invalid certificate ID format', result['message'])
