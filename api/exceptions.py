from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def universal_exception_handler(exc, context):
    """
    Custom exception handler to provide a consistent JSON structure for all API errors.
    Standardizes the error format for both DRF and Django exceptions.
    """
    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    # If an unexpected error occurs (not handled by DRF)
    if response is None:
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'An unexpected server error occurred.',
            'code': 'server_error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Standardize the existing error response
    custom_data = {
        'status': 'error',
        'code': getattr(exc, 'default_code', 'invalid'),
        'message': 'Validation failed' if response.status_code == 400 else str(exc),
        'details': response.data
    }

    # If it's a 404
    if response.status_code == 404:
        custom_data['message'] = 'The requested resource was not found.'
        custom_data['code'] = 'not_found'

    response.data = custom_data
    return response
