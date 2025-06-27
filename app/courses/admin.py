from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment, LessonProgress, CourseReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('title', 'order', 'duration_minutes', 'is_preview')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'is_free', 'is_published', 'student_count', 'created_at')
    list_filter = ('is_published', 'is_free', 'difficulty_level', 'category', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    readonly_fields = ('student_count', 'average_rating', 'lesson_count')
    inlines = [LessonInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'instructor', 'category')
        }),
        ('Course Details', {
            'fields': ('price', 'is_free', 'difficulty_level', 'duration_hours', 'thumbnail')
        }),
        ('Publishing', {
            'fields': ('is_published', 'max_students')
        }),
        ('Statistics', {
            'fields': ('student_count', 'average_rating', 'lesson_count'),
            'classes': ('collapse',)
        })
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration_minutes', 'is_preview', 'created_at')
    list_filter = ('is_preview', 'course__category', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress_percentage', 'is_active', 'enrolled_at', 'completed_at')
    list_filter = ('is_active', 'enrolled_at', 'completed_at', 'course__category')
    search_fields = ('student__username', 'course__title')
    readonly_fields = ('enrolled_at',)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'completed_at', 'watch_time_seconds')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('enrollment__student__username', 'lesson__title')


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'course__category')
    search_fields = ('course__title', 'student__username', 'review_text')
    readonly_fields = ('created_at', 'updated_at')
