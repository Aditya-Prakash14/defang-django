from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import Course


class Quiz(models.Model):
    """Quiz model"""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Quiz settings
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time limit in minutes (leave blank for no limit)"
    )
    passing_score = models.PositiveIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum percentage to pass"
    )
    max_attempts = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of attempts allowed"
    )

    # Quiz status
    is_active = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(
        default=False,
        help_text="Randomize question order for each attempt"
    )
    show_results_immediately = models.BooleanField(
        default=True,
        help_text="Show results immediately after submission"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course', 'title']
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def total_points(self):
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    """Quiz question model"""

    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='multiple_choice'
    )
    points = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    order = models.PositiveIntegerField(default=1)

    # Optional explanation
    explanation = models.TextField(
        blank=True,
        help_text="Explanation shown after answering"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['quiz', 'order']
        unique_together = ['quiz', 'order']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class Answer(models.Model):
    """Answer choices for questions"""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question', 'order']
        unique_together = ['question', 'order']

    def __str__(self):
        return f"{self.question} - {self.answer_text[:50]}"


class QuizAttempt(models.Model):
    """Student quiz attempts"""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )

    # Attempt details
    attempt_number = models.PositiveIntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Scoring
    score = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    total_points_earned = models.PositiveIntegerField(default=0)
    total_points_possible = models.PositiveIntegerField(default=0)

    # Status
    is_completed = models.BooleanField(default=False)
    passed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']
        unique_together = ['quiz', 'student', 'attempt_number']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} (Attempt {self.attempt_number})"

    def calculate_score(self):
        """Calculate the score for this attempt"""
        if not self.is_completed:
            return 0

        total_earned = sum(
            response.points_earned for response in self.responses.all()
        )
        total_possible = self.quiz.total_points

        if total_possible > 0:
            percentage = (total_earned / total_possible) * 100
            self.score = int(percentage)
            self.total_points_earned = total_earned
            self.total_points_possible = total_possible
            self.passed = self.score >= self.quiz.passing_score
            self.save()

        return self.score


class QuizResponse(models.Model):
    """Student responses to quiz questions"""

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    # Response data
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="For multiple choice and true/false questions"
    )
    text_answer = models.TextField(
        blank=True,
        help_text="For short answer questions"
    )

    # Scoring
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveIntegerField(default=0)

    # Timestamps
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question}"

    def check_answer(self):
        """Check if the answer is correct and assign points"""
        if self.question.question_type in ['multiple_choice', 'true_false']:
            if self.selected_answer and self.selected_answer.is_correct:
                self.is_correct = True
                self.points_earned = self.question.points
            else:
                self.is_correct = False
                self.points_earned = 0
        elif self.question.question_type == 'short_answer':
            # For short answer, manual grading might be needed
            # For now, we'll mark it as correct if there's an answer
            self.is_correct = bool(self.text_answer.strip())
            self.points_earned = self.question.points if self.is_correct else 0

        self.save()
        return self.is_correct
