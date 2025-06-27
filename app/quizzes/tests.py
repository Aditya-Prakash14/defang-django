from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from courses.models import Course, Enrollment
from .models import Quiz, Question, Answer, QuizAttempt, QuizResponse

User = get_user_model()


class QuizModelTest(TestCase):
    """Test Quiz model"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            user_type='instructor'
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

        self.quiz_data = {
            'course': self.course,
            'title': 'Python Quiz 1',
            'description': 'Test your Python knowledge',
            'time_limit_minutes': 30,
            'passing_score': 70,
            'max_attempts': 3,
            'is_active': True
        }

    def test_create_quiz(self):
        """Test creating a quiz"""
        quiz = Quiz.objects.create(**self.quiz_data)
        self.assertEqual(quiz.title, 'Python Quiz 1')
        self.assertEqual(quiz.course, self.course)
        self.assertEqual(quiz.passing_score, 70)
        self.assertEqual(quiz.max_attempts, 3)
        self.assertTrue(quiz.is_active)

    def test_quiz_str_representation(self):
        """Test quiz string representation"""
        quiz = Quiz.objects.create(**self.quiz_data)
        expected = f"{self.course.title} - {quiz.title}"
        self.assertEqual(str(quiz), expected)

    def test_quiz_question_count(self):
        """Test quiz question count property"""
        quiz = Quiz.objects.create(**self.quiz_data)
        self.assertEqual(quiz.question_count, 0)

        # Add a question
        Question.objects.create(
            quiz=quiz,
            question_text='What is Python?',
            question_type='multiple_choice',
            points=1,
            order=1
        )

        self.assertEqual(quiz.question_count, 1)


class QuestionModelTest(TestCase):
    """Test Question model"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            user_type='instructor'
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

        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Python Quiz 1',
            description='Test your Python knowledge',
            passing_score=70,
            max_attempts=3,
            is_active=True
        )

    def test_create_question(self):
        """Test creating a question"""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is Python?',
            question_type='multiple_choice',
            points=1,
            order=1
        )

        self.assertEqual(question.question_text, 'What is Python?')
        self.assertEqual(question.question_type, 'multiple_choice')
        self.assertEqual(question.points, 1)
        self.assertEqual(question.quiz, self.quiz)

    def test_question_with_answers(self):
        """Test question with multiple choice answers"""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is Python?',
            question_type='multiple_choice',
            points=1,
            order=1
        )

        # Add answers
        Answer.objects.create(
            question=question,
            answer_text='A programming language',
            is_correct=True,
            order=1
        )

        Answer.objects.create(
            question=question,
            answer_text='A snake',
            is_correct=False,
            order=2
        )

        self.assertEqual(question.answers.count(), 2)
        correct_answer = question.answers.filter(is_correct=True).first()
        self.assertEqual(correct_answer.answer_text, 'A programming language')


class QuizAttemptTest(TestCase):
    """Test Quiz attempt functionality"""

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

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            is_active=True
        )

        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Python Quiz 1',
            description='Test your Python knowledge',
            passing_score=70,
            max_attempts=3,
            is_active=True
        )

        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is Python?',
            question_type='multiple_choice',
            points=10,
            order=1
        )

        self.correct_answer = Answer.objects.create(
            question=self.question,
            answer_text='A programming language',
            is_correct=True,
            order=1
        )

        self.wrong_answer = Answer.objects.create(
            question=self.question,
            answer_text='A snake',
            is_correct=False,
            order=2
        )

    def test_create_quiz_attempt(self):
        """Test creating a quiz attempt"""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            student=self.student,
            attempt_number=1
        )

        self.assertEqual(attempt.quiz, self.quiz)
        self.assertEqual(attempt.student, self.student)
        self.assertEqual(attempt.attempt_number, 1)
        self.assertFalse(attempt.is_completed)
        self.assertFalse(attempt.passed)

    def test_quiz_response_correct_answer(self):
        """Test quiz response with correct answer"""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            student=self.student,
            attempt_number=1
        )

        response = QuizResponse.objects.create(
            attempt=attempt,
            question=self.question,
            selected_answer=self.correct_answer
        )

        # Check answer
        is_correct = response.check_answer()
        self.assertTrue(is_correct)
        self.assertTrue(response.is_correct)
        self.assertEqual(response.points_earned, 10)

    def test_quiz_response_wrong_answer(self):
        """Test quiz response with wrong answer"""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            student=self.student,
            attempt_number=1
        )

        response = QuizResponse.objects.create(
            attempt=attempt,
            question=self.question,
            selected_answer=self.wrong_answer
        )

        # Check answer
        is_correct = response.check_answer()
        self.assertFalse(is_correct)
        self.assertFalse(response.is_correct)
        self.assertEqual(response.points_earned, 0)
