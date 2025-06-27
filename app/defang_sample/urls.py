"""
URL configuration for defang_sample project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check endpoint (simple, no dependencies)
    path('health/', lambda request: JsonResponse({'status': 'ok', 'method': request.method})),

    # API endpoints
    path('api/', include('api.urls', namespace='api')),
    path('api/auth/', include('users.urls', namespace='users')),
    path('api/courses/', include('courses.urls', namespace='courses')),
    path('api/quizzes/', include('quizzes.urls', namespace='quizzes')),
    path('api/certificates/', include('certificates.urls', namespace='certificates')),

    # Legacy endpoints
    path('todos/', include('example_app.urls', namespace='example_app')),
    path('', RedirectView.as_view(url='/todos/')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
