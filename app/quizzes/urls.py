from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    # Course quizzes
    path('courses/<int:course_id>/quizzes/', views.CourseQuizListView.as_view(), name='course_quiz_list'),
    path('courses/<int:course_id>/quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    
    # Quiz questions (instructor only)
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/questions/', views.QuizQuestionListView.as_view(), name='quiz_questions'),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    
    # Quiz taking (students)
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/start/', views.start_quiz_attempt, name='start_quiz'),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/attempts/<int:attempt_id>/submit/', views.submit_quiz_attempt, name='submit_quiz'),
    
    # Quiz attempts
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/attempts/', views.StudentQuizAttemptListView.as_view(), name='student_quiz_attempts'),
    path('attempts/<int:pk>/', views.QuizAttemptDetailView.as_view(), name='quiz_attempt_detail'),
    
    # Instructor views
    path('instructor/courses/<int:course_id>/quiz-attempts/', views.InstructorQuizAttemptListView.as_view(), name='instructor_quiz_attempts'),
    path('instructor/courses/<int:course_id>/quizzes/<int:quiz_id>/attempts/', views.InstructorQuizAttemptListView.as_view(), name='instructor_quiz_attempts_by_quiz'),
    
    # Student dashboard
    path('my-attempts/', views.StudentQuizAttemptListView.as_view(), name='my_quiz_attempts'),
]
