import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Standardizes error responses across all DRF views.
    Returns:
    {
        "success": false,
        "status_code": <status_code>,
        "error": "<summary error message>",
        "details": <detailed field errors or messages>
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_message = "Validation or processing error"
        if isinstance(response.data, dict) and 'detail' in response.data:
            error_message = str(response.data['detail'])
        elif isinstance(response.data, list) and len(response.data) > 0:
            error_message = str(response.data[0])
        elif isinstance(response.data, dict):
            # Extract first field error if available
            first_field = next(iter(response.data))
            first_val = response.data[first_field]
            if isinstance(first_val, list) and len(first_val) > 0:
                error_message = f"{first_field}: {first_val[0]}"
            else:
                error_message = f"{first_field}: {first_val}"

        response.data = {
            'success': False,
            'status_code': response.status_code,
            'error': error_message,
            'details': response.data
        }
    return response
