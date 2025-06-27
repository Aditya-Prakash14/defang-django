from rest_framework import serializers
from .models import Category, Course, Lesson, Enrollment, LessonProgress, CourseReview
from users.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for course categories"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for lessons"""
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'order', 'video_file',
            'video_url', 'pdf_material', 'duration_minutes',
            'is_preview', 'created_at', 'updated_at'
        ]


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list view"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    student_count = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    lesson_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor_name', 'category_name',
            'price', 'is_free', 'difficulty_level', 'duration_hours',
            'thumbnail', 'is_published', 'student_count', 'average_rating',
            'lesson_count', 'created_at'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course detail view"""
    instructor = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    student_count = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    lesson_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor', 'category',
            'price', 'is_free', 'difficulty_level', 'duration_hours',
            'thumbnail', 'is_published', 'max_students', 'lessons',
            'student_count', 'average_rating', 'lesson_count',
            'created_at', 'updated_at'
        ]


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating courses"""
    
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'category', 'price', 'is_free',
            'difficulty_level', 'duration_hours', 'thumbnail',
            'is_published', 'max_students'
        ]
    
    def create(self, validated_data):
        # Set the instructor to the current user
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class LessonCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating lessons"""
    
    class Meta:
        model = Lesson
        fields = [
            'title', 'description', 'order', 'video_file',
            'video_url', 'pdf_material', 'duration_minutes', 'is_preview'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for course enrollments"""
    course = CourseListSerializer(read_only=True)
    student = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'enrolled_at', 'is_active',
            'progress_percentage', 'completed_at', 'amount_paid'
        ]


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for lesson progress tracking"""
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'is_completed', 'completed_at', 'watch_time_seconds'
        ]


class CourseReviewSerializer(serializers.ModelSerializer):
    """Serializer for course reviews"""
    student = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = CourseReview
        fields = [
            'id', 'student', 'rating', 'review_text', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class CourseReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating course reviews"""
    
    class Meta:
        model = CourseReview
        fields = ['rating', 'review_text']
