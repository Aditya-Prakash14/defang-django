from rest_framework import serializers
from .models import Certificate, CertificateTemplate
from users.serializers import UserProfileSerializer
from courses.serializers import CourseListSerializer


class CertificateTemplateSerializer(serializers.ModelSerializer):
    """Serializer for certificate templates"""
    
    class Meta:
        model = CertificateTemplate
        fields = [
            'id', 'name', 'description', 'background_color',
            'text_color', 'border_color', 'logo', 'background_image',
            'title_font_size', 'body_font_size', 'is_active',
            'is_default', 'created_at', 'updated_at'
        ]


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for certificates"""
    student = UserProfileSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    instructor_name = serializers.CharField(source='course.instructor.get_full_name', read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_id', 'student', 'course', 'student_name',
            'course_title', 'instructor_name', 'issued_date', 'completion_date',
            'final_score', 'pdf_file', 'is_verified', 'verification_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'certificate_id', 'issued_date', 'verification_code',
            'created_at', 'updated_at'
        ]


class CertificateListSerializer(serializers.ModelSerializer):
    """Serializer for certificate list view"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    instructor_name = serializers.CharField(source='course.instructor.get_full_name', read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_id', 'student_name', 'course_title',
            'instructor_name', 'issued_date', 'completion_date',
            'final_score', 'is_verified'
        ]


class CertificateVerificationSerializer(serializers.Serializer):
    """Serializer for certificate verification"""
    certificate_id = serializers.UUIDField(required=False)
    verification_code = serializers.CharField(max_length=50, required=False)
    
    def validate(self, attrs):
        if not attrs.get('certificate_id') and not attrs.get('verification_code'):
            raise serializers.ValidationError(
                "Either certificate_id or verification_code is required"
            )
        return attrs


class CertificateVerificationResultSerializer(serializers.Serializer):
    """Serializer for certificate verification results"""
    valid = serializers.BooleanField()
    message = serializers.CharField(required=False)
    student_name = serializers.CharField(required=False)
    course_title = serializers.CharField(required=False)
    completion_date = serializers.DateTimeField(required=False)
    final_score = serializers.IntegerField(required=False)
    issued_date = serializers.DateTimeField(required=False)
