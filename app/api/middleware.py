import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from rest_framework import status


class APIErrorHandlingMiddleware:
    """
    Middleware to handle API errors consistently
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """
        Handle exceptions for API requests
        """
        if not request.path.startswith('/api/'):
            return None
        
        if isinstance(exception, ValidationError):
            return JsonResponse({
                'error': 'Validation error',
                'details': exception.message_dict if hasattr(exception, 'message_dict') else str(exception)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # For other exceptions in production, return generic error
        # In development, you might want to return more details
        return JsonResponse({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
