from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('health/', views.health_check, name='health_check'),
    path('stats/', views.platform_stats, name='platform_stats'),
]
