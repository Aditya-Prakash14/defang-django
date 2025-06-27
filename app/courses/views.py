from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Category, Course, Lesson, Enrollment, LessonProgress, CourseReview
from django.db import models
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseCreateUpdateSerializer, LessonSerializer, LessonCreateUpdateSerializer,
    EnrollmentSerializer, LessonProgressSerializer, CourseReviewSerializer,
    CourseReviewCreateSerializer
)


class CategoryListView(generics.ListCreateAPIView):
    """List and create course categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]


class CourseListView(generics.ListAPIView):
    """List all published courses"""
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__icontains=category)

        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)

        # Filter by price (free/paid)
        is_free = self.request.query_params.get('is_free')
        if is_free is not None:
            queryset = queryset.filter(is_free=is_free.lower() == 'true')

        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )

        return queryset


class CourseDetailView(generics.RetrieveAPIView):
    """Get course details"""
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]


class InstructorCourseListView(generics.ListCreateAPIView):
    """List instructor's courses and create new courses"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateUpdateSerializer
        return CourseListSerializer

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)

    def perform_create(self, serializer):
        # Only instructors can create courses
        if not self.request.user.is_instructor:
            raise permissions.PermissionDenied("Only instructors can create courses")
        serializer.save(instructor=self.request.user)


class InstructorCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Instructor course management"""
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class CourseLessonListView(generics.ListCreateAPIView):
    """List and create lessons for a course"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonCreateUpdateSerializer
        return LessonSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Check if user is instructor or enrolled student
        if self.request.user == course.instructor:
            return course.lessons.all()
        elif course.enrollments.filter(student=self.request.user, is_active=True).exists():
            return course.lessons.all()
        else:
            # Only show preview lessons for non-enrolled users
            return course.lessons.filter(is_preview=True)

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id, instructor=self.request.user)
        serializer.save(course=course)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Lesson detail view for instructors"""
    serializer_class = LessonCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Lesson.objects.filter(
            course_id=course_id,
            course__instructor=self.request.user
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_in_course(request, course_id):
    """Enroll student in a course"""
    course = get_object_or_404(Course, id=course_id, is_published=True)

    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return Response(
            {'error': 'Already enrolled in this course'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if course has max students limit
    if course.max_students and course.student_count >= course.max_students:
        return Response(
            {'error': 'Course is full'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create enrollment
    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course,
        amount_paid=0 if course.is_free else course.price
    )

    return Response(
        {
            'message': 'Successfully enrolled in course',
            'enrollment': EnrollmentSerializer(enrollment).data
        },
        status=status.HTTP_201_CREATED
    )


class StudentEnrollmentListView(generics.ListAPIView):
    """List student's enrollments"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user,
            is_active=True
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_lesson_complete(request, course_id, lesson_id):
    """Mark a lesson as completed"""
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course=course,
        is_active=True
    )

    # Create or update lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={
            'is_completed': True,
            'completed_at': timezone.now()
        }
    )

    if not created and not lesson_progress.is_completed:
        lesson_progress.is_completed = True
        lesson_progress.completed_at = timezone.now()
        lesson_progress.save()

    # Update overall course progress
    total_lessons = course.lessons.count()
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        is_completed=True
    ).count()

    progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    enrollment.progress_percentage = int(progress_percentage)

    if progress_percentage == 100:
        enrollment.completed_at = timezone.now()

    enrollment.save()

    return Response(
        {
            'message': 'Lesson marked as completed',
            'progress_percentage': enrollment.progress_percentage
        },
        status=status.HTTP_200_OK
    )


class CourseReviewListView(generics.ListCreateAPIView):
    """List and create course reviews"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseReviewCreateSerializer
        return CourseReviewSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return CourseReview.objects.filter(course_id=course_id)

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Check if user is enrolled in the course
        if not Enrollment.objects.filter(
            student=self.request.user,
            course=course,
            is_active=True
        ).exists():
            raise permissions.PermissionDenied("Must be enrolled to review course")

        serializer.save(student=self.request.user, course=course)


class StudentProgressView(generics.RetrieveAPIView):
    """Get student's progress in a specific course"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        course_id = self.kwargs['course_id']
        return get_object_or_404(
            Enrollment,
            course_id=course_id,
            student=self.request.user,
            is_active=True
        )


class StudentDashboardView(generics.ListAPIView):
    """Student dashboard showing all enrollments and progress"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user,
            is_active=True
        ).select_related('course').prefetch_related('lesson_progress')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_progress_detail(request, course_id):
    """Get detailed progress for a course including lesson progress"""
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(
        Enrollment,
        course=course,
        student=request.user,
        is_active=True
    )

    # Get lesson progress
    lesson_progress = LessonProgress.objects.filter(
        enrollment=enrollment
    ).select_related('lesson')

    # Serialize data
    enrollment_data = EnrollmentSerializer(enrollment).data
    lesson_progress_data = LessonProgressSerializer(lesson_progress, many=True).data

    return Response({
        'enrollment': enrollment_data,
        'lesson_progress': lesson_progress_data,
        'total_lessons': course.lessons.count(),
        'completed_lessons': lesson_progress.filter(is_completed=True).count()
    })


class InstructorCourseAnalyticsView(generics.RetrieveAPIView):
    """Analytics for instructor's course"""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        course_id = self.kwargs['course_id']
        return get_object_or_404(
            Course,
            id=course_id,
            instructor=self.request.user
        )

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()

        # Get enrollment statistics
        enrollments = course.enrollments.filter(is_active=True)
        total_students = enrollments.count()
        completed_students = enrollments.filter(progress_percentage=100).count()

        # Get lesson completion rates
        lessons = course.lessons.all()
        lesson_stats = []

        for lesson in lessons:
            completed_count = LessonProgress.objects.filter(
                lesson=lesson,
                is_completed=True
            ).count()

            lesson_stats.append({
                'lesson_id': lesson.id,
                'lesson_title': lesson.title,
                'completion_rate': (completed_count / total_students * 100) if total_students > 0 else 0,
                'completed_count': completed_count
            })

        # Get quiz statistics
        quiz_stats = []
        for quiz in course.quizzes.all():
            attempts = quiz.attempts.filter(is_completed=True)
            passed_attempts = attempts.filter(passed=True)

            quiz_stats.append({
                'quiz_id': quiz.id,
                'quiz_title': quiz.title,
                'total_attempts': attempts.count(),
                'passed_attempts': passed_attempts.count(),
                'pass_rate': (passed_attempts.count() / attempts.count() * 100) if attempts.count() > 0 else 0,
                'average_score': attempts.aggregate(avg_score=models.Avg('score'))['avg_score'] or 0
            })

        return Response({
            'course': {
                'id': course.id,
                'title': course.title,
                'total_students': total_students,
                'completed_students': completed_students,
                'completion_rate': (completed_students / total_students * 100) if total_students > 0 else 0
            },
            'lesson_statistics': lesson_stats,
            'quiz_statistics': quiz_stats
        })
