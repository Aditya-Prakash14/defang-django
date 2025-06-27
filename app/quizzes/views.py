from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from courses.models import Course
from .models import Quiz, Question, QuizAttempt, QuizResponse
from .serializers import (
    QuizListSerializer, QuizDetailSerializer, QuizCreateUpdateSerializer,
    QuestionDetailSerializer, QuestionCreateUpdateSerializer,
    QuizAttemptSerializer, QuizAttemptDetailSerializer,
    QuizSubmissionSerializer
)


class CourseQuizListView(generics.ListCreateAPIView):
    """List and create quizzes for a course"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizCreateUpdateSerializer
        return QuizListSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Check if user is instructor or enrolled student
        if self.request.user == course.instructor:
            return course.quizzes.all()
        elif course.enrollments.filter(student=self.request.user, is_active=True).exists():
            return course.quizzes.filter(is_active=True)
        else:
            return Quiz.objects.none()

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id, instructor=self.request.user)
        serializer.save(course=course)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Quiz detail view"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QuizCreateUpdateSerializer
        return QuizDetailSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Check permissions
        if self.request.user == course.instructor:
            return course.quizzes.all()
        elif course.enrollments.filter(student=self.request.user, is_active=True).exists():
            return course.quizzes.filter(is_active=True)
        else:
            return Quiz.objects.none()


class QuizQuestionListView(generics.ListCreateAPIView):
    """List and create questions for a quiz"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionCreateUpdateSerializer
        return QuestionDetailSerializer

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Only quiz creator (instructor) can see all questions with answers
        if self.request.user == quiz.course.instructor:
            return quiz.questions.all()
        else:
            return Question.objects.none()

    def perform_create(self, serializer):
        quiz_id = self.kwargs['quiz_id']
        quiz = get_object_or_404(Quiz, id=quiz_id, course__instructor=self.request.user)
        serializer.save(quiz=quiz)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Question detail view for instructors"""
    serializer_class = QuestionCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        return Question.objects.filter(
            quiz_id=quiz_id,
            quiz__course__instructor=self.request.user
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz_attempt(request, course_id, quiz_id):
    """Start a new quiz attempt"""
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course, is_active=True)

    # Check if user is enrolled
    if not course.enrollments.filter(student=request.user, is_active=True).exists():
        return Response(
            {'error': 'Must be enrolled in course to take quiz'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check attempt limit
    existing_attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        student=request.user
    ).count()

    if existing_attempts >= quiz.max_attempts:
        return Response(
            {'error': 'Maximum attempts reached'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create new attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        student=request.user,
        attempt_number=existing_attempts + 1
    )

    return Response(
        {
            'attempt_id': attempt.id,
            'message': 'Quiz attempt started',
            'time_limit_minutes': quiz.time_limit_minutes
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_attempt(request, course_id, quiz_id, attempt_id):
    """Submit quiz attempt with answers"""
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        quiz=quiz,
        student=request.user,
        is_completed=False
    )

    serializer = QuizSubmissionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        # Process each response
        for response_data in serializer.validated_data['responses']:
            question = get_object_or_404(Question, id=response_data['question'].id, quiz=quiz)

            # Create or update response
            response, created = QuizResponse.objects.get_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    'selected_answer': response_data.get('selected_answer'),
                    'text_answer': response_data.get('text_answer', '')
                }
            )

            if not created:
                response.selected_answer = response_data.get('selected_answer')
                response.text_answer = response_data.get('text_answer', '')
                response.save()

            # Check answer and assign points
            response.check_answer()

        # Mark attempt as completed
        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        # Calculate final score
        final_score = attempt.calculate_score()

    # Prepare response data
    response_data = {
        'message': 'Quiz submitted successfully',
        'score': final_score,
        'passed': attempt.passed,
        'total_points_earned': attempt.total_points_earned,
        'total_points_possible': attempt.total_points_possible
    }

    # Include detailed results if enabled
    if quiz.show_results_immediately:
        response_data['attempt'] = QuizAttemptDetailSerializer(attempt).data

    return Response(response_data, status=status.HTTP_200_OK)


class StudentQuizAttemptListView(generics.ListAPIView):
    """List student's quiz attempts"""
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        quiz_id = self.kwargs.get('quiz_id')

        queryset = QuizAttempt.objects.filter(student=self.request.user)

        if course_id:
            queryset = queryset.filter(quiz__course_id=course_id)

        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

        return queryset


class QuizAttemptDetailView(generics.RetrieveAPIView):
    """View quiz attempt details"""
    serializer_class = QuizAttemptDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Students can only see their own attempts
        # Instructors can see all attempts for their quizzes
        if hasattr(self, 'kwargs') and 'course_id' in self.kwargs:
            course_id = self.kwargs['course_id']
            course = get_object_or_404(Course, id=course_id)

            if self.request.user == course.instructor:
                return QuizAttempt.objects.filter(quiz__course=course)

        return QuizAttempt.objects.filter(student=self.request.user)


class InstructorQuizAttemptListView(generics.ListAPIView):
    """List all attempts for instructor's quizzes"""
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        quiz_id = self.kwargs.get('quiz_id')

        queryset = QuizAttempt.objects.filter(quiz__course__instructor=self.request.user)

        if course_id:
            queryset = queryset.filter(quiz__course_id=course_id)

        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

        return queryset
