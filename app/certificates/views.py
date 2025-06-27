from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from courses.models import Course, Enrollment
from .models import Certificate
from .serializers import (
    CertificateSerializer, CertificateListSerializer,
    CertificateVerificationSerializer, CertificateVerificationResultSerializer
)
from .utils import generate_certificate_for_enrollment, verify_certificate


class StudentCertificateListView(generics.ListAPIView):
    """List student's certificates"""
    serializer_class = CertificateListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(
            student=self.request.user,
            is_verified=True
        )


class CertificateDetailView(generics.RetrieveAPIView):
    """Get certificate details"""
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(
            student=self.request.user,
            is_verified=True
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_certificate(request, course_id):
    """Generate certificate for completed course"""
    course = get_object_or_404(Course, id=course_id)

    # Check if user is enrolled and completed the course
    try:
        enrollment = Enrollment.objects.get(
            student=request.user,
            course=course,
            is_active=True,
            progress_percentage=100
        )
    except Enrollment.DoesNotExist:
        return Response(
            {'error': 'Course not completed or not enrolled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if certificate already exists
    if hasattr(enrollment, 'certificate'):
        return Response(
            {
                'message': 'Certificate already exists',
                'certificate': CertificateSerializer(enrollment.certificate).data
            },
            status=status.HTTP_200_OK
        )

    # Generate certificate
    try:
        certificate = generate_certificate_for_enrollment(enrollment)
        return Response(
            {
                'message': 'Certificate generated successfully',
                'certificate': CertificateSerializer(certificate).data
            },
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to generate certificate: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_certificate(request, certificate_id):
    """Download certificate PDF"""
    certificate = get_object_or_404(
        Certificate,
        certificate_id=certificate_id,
        student=request.user,
        is_verified=True
    )

    if not certificate.pdf_file:
        return Response(
            {'error': 'Certificate PDF not available'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        response = HttpResponse(
            certificate.pdf_file.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_id}.pdf"'
        return response
    except Exception as e:
        return Response(
            {'error': f'Failed to download certificate: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_certificate_view(request):
    """Verify a certificate by ID or verification code"""
    serializer = CertificateVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    certificate_id = serializer.validated_data.get('certificate_id')
    verification_code = serializer.validated_data.get('verification_code')

    result = verify_certificate(certificate_id, verification_code)

    result_serializer = CertificateVerificationResultSerializer(data=result)
    result_serializer.is_valid(raise_exception=True)

    return Response(result_serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def public_certificate_view(request, certificate_id):
    """Public view of certificate for verification"""
    try:
        certificate = Certificate.objects.get(
            certificate_id=certificate_id,
            is_verified=True
        )

        return Response({
            'valid': True,
            'student_name': certificate.student.get_full_name() or certificate.student.username,
            'course_title': certificate.course.title,
            'instructor_name': certificate.course.instructor.get_full_name() or certificate.course.instructor.username,
            'completion_date': certificate.completion_date,
            'final_score': certificate.final_score,
            'issued_date': certificate.issued_date,
            'verification_code': certificate.verification_code
        }, status=status.HTTP_200_OK)

    except Certificate.DoesNotExist:
        return Response(
            {'valid': False, 'message': 'Certificate not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class InstructorCertificateListView(generics.ListAPIView):
    """List certificates for instructor's courses"""
    serializer_class = CertificateListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(
            course__instructor=self.request.user,
            is_verified=True
        )


class CourseCertificateListView(generics.ListAPIView):
    """List certificates for a specific course"""
    serializer_class = CertificateListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)

        # Check if user is instructor
        if self.request.user != course.instructor:
            return Certificate.objects.none()

        return Certificate.objects.filter(
            course=course,
            is_verified=True
        )
