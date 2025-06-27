from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, QuizResponse


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2
    fields = ('answer_text', 'is_correct', 'order')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('question_text', 'question_type', 'points', 'order')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'passing_score', 'max_attempts', 'question_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'course__category', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    readonly_fields = ('question_count', 'total_points')
    inlines = [QuestionInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description')
        }),
        ('Quiz Settings', {
            'fields': ('time_limit_minutes', 'passing_score', 'max_attempts')
        }),
        ('Display Options', {
            'fields': ('randomize_questions', 'show_results_immediately', 'is_active')
        }),
        ('Statistics', {
            'fields': ('question_count', 'total_points'),
            'classes': ('collapse',)
        })
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text_short', 'question_type', 'points', 'order', 'created_at')
    list_filter = ('question_type', 'quiz__course__category', 'created_at')
    search_fields = ('question_text', 'quiz__title')
    ordering = ('quiz', 'order')
    inlines = [AnswerInline]

    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = "Question"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer_text_short', 'is_correct', 'order', 'created_at')
    list_filter = ('is_correct', 'question__question_type', 'created_at')
    search_fields = ('answer_text', 'question__question_text')
    ordering = ('question', 'order')

    def answer_text_short(self, obj):
        return obj.answer_text[:50] + "..." if len(obj.answer_text) > 50 else obj.answer_text
    answer_text_short.short_description = "Answer"


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'attempt_number', 'score', 'passed', 'is_completed', 'started_at', 'completed_at')
    list_filter = ('is_completed', 'passed', 'quiz__course__category', 'started_at')
    search_fields = ('student__username', 'quiz__title')
    readonly_fields = ('started_at', 'score', 'total_points_earned', 'total_points_possible', 'passed')
    ordering = ('-started_at',)


@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'points_earned', 'answered_at')
    list_filter = ('is_correct', 'question__question_type', 'answered_at')
    search_fields = ('attempt__student__username', 'question__question_text')
    readonly_fields = ('answered_at', 'is_correct', 'points_earned')
    ordering = ('-answered_at',)
