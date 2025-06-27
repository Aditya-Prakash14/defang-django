from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.urls import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root - Lists all available endpoints
    """
    return Response({
        'message': 'Welcome to the E-Learning Platform API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': request.build_absolute_uri('/api/auth/register/'),
                'login': request.build_absolute_uri('/api/auth/login/'),
                'token_refresh': request.build_absolute_uri('/api/auth/token/refresh/'),
                'profile': request.build_absolute_uri('/api/auth/profile/'),
                'users': request.build_absolute_uri('/api/auth/users/'),
            },
            'courses': {
                'categories': request.build_absolute_uri('/api/courses/categories/'),
                'courses': request.build_absolute_uri('/api/courses/'),
                'enrollments': request.build_absolute_uri('/api/courses/enrollments/'),
                'dashboard': request.build_absolute_uri('/api/courses/dashboard/'),
                'instructor_courses': request.build_absolute_uri('/api/courses/instructor/courses/'),
            },
            'quizzes': {
                'my_attempts': request.build_absolute_uri('/api/quizzes/my-attempts/'),
            },
            'certificates': {
                'my_certificates': request.build_absolute_uri('/api/certificates/my-certificates/'),
                'verify': request.build_absolute_uri('/api/certificates/verify/'),
            }
        },
        'documentation': 'See api_documentation.md for detailed API documentation',
        'authentication': 'JWT Bearer token required for most endpoints',
        'content_type': 'application/json'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint
    """
    return Response({
        'status': 'healthy',
        'message': 'E-Learning Platform API is running',
        'timestamp': request.META.get('HTTP_DATE', 'N/A')
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def platform_stats(request):
    """
    Get platform statistics
    """
    from users.models import User
    from courses.models import Course, Enrollment
    from quizzes.models import Quiz, QuizAttempt
    from certificates.models import Certificate

    stats = {
        'users': {
            'total': User.objects.count(),
            'students': User.objects.filter(user_type='student').count(),
            'instructors': User.objects.filter(user_type='instructor').count(),
        },
        'courses': {
            'total': Course.objects.count(),
            'published': Course.objects.filter(is_published=True).count(),
            'free': Course.objects.filter(is_free=True).count(),
        },
        'enrollments': {
            'total': Enrollment.objects.filter(is_active=True).count(),
            'completed': Enrollment.objects.filter(progress_percentage=100).count(),
        },
        'quizzes': {
            'total': Quiz.objects.filter(is_active=True).count(),
            'attempts': QuizAttempt.objects.filter(is_completed=True).count(),
        },
        'certificates': {
            'issued': Certificate.objects.filter(is_verified=True).count(),
        }
    }

    return Response(stats)
