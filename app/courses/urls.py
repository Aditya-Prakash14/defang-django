from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    
    # Public course endpoints
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_in_course, name='enroll_course'),
    
    # Course lessons
    path('<int:course_id>/lessons/', views.CourseLessonListView.as_view(), name='course_lessons'),
    path('<int:course_id>/lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('<int:course_id>/lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    
    # Course reviews
    path('<int:course_id>/reviews/', views.CourseReviewListView.as_view(), name='course_reviews'),
    
    # Instructor endpoints
    path('instructor/courses/', views.InstructorCourseListView.as_view(), name='instructor_courses'),
    path('instructor/courses/<int:pk>/', views.InstructorCourseDetailView.as_view(), name='instructor_course_detail'),
    
    # Student enrollments and progress
    path('enrollments/', views.StudentEnrollmentListView.as_view(), name='student_enrollments'),
    path('<int:course_id>/progress/', views.StudentProgressView.as_view(), name='student_progress'),
    path('<int:course_id>/progress/detail/', views.course_progress_detail, name='course_progress_detail'),
    path('dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),

    # Instructor analytics
    path('instructor/courses/<int:course_id>/analytics/', views.InstructorCourseAnalyticsView.as_view(), name='course_analytics'),
]
