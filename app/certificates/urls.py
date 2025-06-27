from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    # Student certificate endpoints
    path('my-certificates/', views.StudentCertificateListView.as_view(), name='my_certificates'),
    path('<uuid:pk>/', views.CertificateDetailView.as_view(), name='certificate_detail'),
    path('generate/<int:course_id>/', views.generate_certificate, name='generate_certificate'),
    path('download/<uuid:certificate_id>/', views.download_certificate, name='download_certificate'),
    
    # Certificate verification
    path('verify/', views.verify_certificate_view, name='verify_certificate'),
    path('public/<uuid:certificate_id>/', views.public_certificate_view, name='public_certificate'),
    
    # Instructor certificate endpoints
    path('instructor/certificates/', views.InstructorCertificateListView.as_view(), name='instructor_certificates'),
    path('instructor/courses/<int:course_id>/certificates/', views.CourseCertificateListView.as_view(), name='course_certificates'),
]
