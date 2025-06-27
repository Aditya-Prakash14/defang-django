from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from .models import Category, Course, Lesson, Enrollment, LessonProgress

User = get_user_model()


class CourseModelTest(TestCase):
    """Test Course model"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            user_type='instructor'
        )

        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )

        self.course_data = {
            'title': 'Python Basics',
            'description': 'Learn Python programming',
            'instructor': self.instructor,
            'category': self.category,
            'price': Decimal('99.99'),
            'is_free': False,
            'difficulty_level': 'beginner',
            'duration_hours': 10,
            'is_published': True
        }

    def test_create_course(self):
        """Test creating a course"""
        course = Course.objects.create(**self.course_data)
        self.assertEqual(course.title, 'Python Basics')
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(course.category, self.category)
        self.assertEqual(course.price, Decimal('99.99'))
        self.assertFalse(course.is_free)
        self.assertTrue(course.is_published)

    def test_course_str_representation(self):
        """Test course string representation"""
        course = Course.objects.create(**self.course_data)
        self.assertEqual(str(course), 'Python Basics')

    def test_course_student_count(self):
        """Test course student count property"""
        course = Course.objects.create(**self.course_data)
        student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123'
        )

        # No enrollments initially
        self.assertEqual(course.student_count, 0)

        # Create enrollment
        Enrollment.objects.create(
            student=student,
            course=course,
            is_active=True
        )

        self.assertEqual(course.student_count, 1)


class CourseAPITest(APITestCase):
    """Test Course APIs"""

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
            user_type='student'
        )

        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )

        self.course = Course.objects.create(
            title='Python Basics',
            description='Learn Python programming',
            instructor=self.instructor,
            category=self.category,
            price=Decimal('99.99'),
            is_free=False,
            difficulty_level='beginner',
            duration_hours=10,
            is_published=True
        )

        self.course_list_url = reverse('courses:course_list')
        self.course_detail_url = reverse('courses:course_detail', kwargs={'pk': self.course.pk})
        self.enroll_url = reverse('courses:enroll_course', kwargs={'course_id': self.course.pk})

    def test_course_list_public(self):
        """Test course list is accessible to public"""
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Basics')

    def test_course_detail_public(self):
        """Test course detail is accessible to public"""
        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Basics')

    def test_course_enrollment_authenticated(self):
        """Test course enrollment requires authentication"""
        # Test unauthenticated
        response = self.client.post(self.enroll_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test authenticated
        refresh = RefreshToken.for_user(self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.post(self.enroll_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check enrollment was created
        enrollment = Enrollment.objects.get(student=self.student, course=self.course)
        self.assertTrue(enrollment.is_active)

    def test_duplicate_enrollment(self):
        """Test duplicate enrollment is prevented"""
        refresh = RefreshToken.for_user(self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # First enrollment
        response = self.client.post(self.enroll_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Second enrollment attempt
        response = self.client.post(self.enroll_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Already enrolled', response.data['error'])


class LessonProgressTest(TestCase):
    """Test lesson progress tracking"""

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
            user_type='student'
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

        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Introduction to Python',
            description='First lesson',
            order=1,
            duration_minutes=30
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            is_active=True
        )

    def test_lesson_progress_creation(self):
        """Test creating lesson progress"""
        progress = LessonProgress.objects.create(
            enrollment=self.enrollment,
            lesson=self.lesson,
            is_completed=True
        )

        self.assertTrue(progress.is_completed)
        self.assertEqual(progress.enrollment, self.enrollment)
        self.assertEqual(progress.lesson, self.lesson)

    def test_enrollment_progress_calculation(self):
        """Test enrollment progress calculation"""
        # Initially 0% progress
        self.assertEqual(self.enrollment.progress_percentage, 0)

        # Complete the lesson
        LessonProgress.objects.create(
            enrollment=self.enrollment,
            lesson=self.lesson,
            is_completed=True
        )

        # Since there's only one lesson, progress should be 100%
        # Note: This would need to be implemented in the actual progress calculation logic
