from rest_framework import serializers
from .models import Quiz, Question, Answer, QuizAttempt, QuizResponse


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for answer choices"""
    
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'order']


class AnswerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating answer choices (includes is_correct for instructors)"""
    
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for quiz questions (student view)"""
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_type', 'points',
            'order', 'answers'
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Serializer for question details (instructor view)"""
    answers = AnswerCreateSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_type', 'points',
            'order', 'explanation', 'answers', 'created_at', 'updated_at'
        ]


class QuestionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating questions"""
    answers = AnswerCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Question
        fields = [
            'question_text', 'question_type', 'points', 'order',
            'explanation', 'answers'
        ]
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        question = Question.objects.create(**validated_data)
        
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        
        return question
    
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])
        
        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update answers
        if answers_data:
            # Delete existing answers and create new ones
            instance.answers.all().delete()
            for answer_data in answers_data:
                Answer.objects.create(question=instance, **answer_data)
        
        return instance


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for quiz list view"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    question_count = serializers.ReadOnlyField()
    total_points = serializers.ReadOnlyField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course_title',
            'time_limit_minutes', 'passing_score', 'max_attempts',
            'question_count', 'total_points', 'is_active', 'created_at'
        ]


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for quiz detail view"""
    questions = QuestionSerializer(many=True, read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    question_count = serializers.ReadOnlyField()
    total_points = serializers.ReadOnlyField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course_title',
            'time_limit_minutes', 'passing_score', 'max_attempts',
            'randomize_questions', 'show_results_immediately',
            'questions', 'question_count', 'total_points',
            'is_active', 'created_at', 'updated_at'
        ]


class QuizCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating quizzes"""
    
    class Meta:
        model = Quiz
        fields = [
            'title', 'description', 'time_limit_minutes', 'passing_score',
            'max_attempts', 'randomize_questions', 'show_results_immediately',
            'is_active'
        ]


class QuizResponseSerializer(serializers.ModelSerializer):
    """Serializer for quiz responses"""
    
    class Meta:
        model = QuizResponse
        fields = ['question', 'selected_answer', 'text_answer']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for quiz attempts"""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz_title', 'student_name', 'attempt_number',
            'started_at', 'completed_at', 'score', 'total_points_earned',
            'total_points_possible', 'is_completed', 'passed'
        ]


class QuizAttemptDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed quiz attempt view"""
    responses = QuizResponseSerializer(many=True, read_only=True)
    quiz = QuizDetailSerializer(read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'attempt_number', 'started_at', 'completed_at',
            'score', 'total_points_earned', 'total_points_possible',
            'is_completed', 'passed', 'responses'
        ]


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for quiz submission"""
    responses = QuizResponseSerializer(many=True)
    
    def validate_responses(self, value):
        if not value:
            raise serializers.ValidationError("At least one response is required")
        return value
