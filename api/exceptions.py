from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    error_response = {
        "error": {
            "code": None,
            "message": None,
        }
    }

    # Handle custom 409 conflict
    if isinstance(exc, AlreadyExistsConflictException):
        print("yes got it AlreadyExistsConflictException")
        error_response["error"]["code"] = "conflict"
        error_response["error"]["message"] = str(exc.detail)
        response.data = error_response
        response.status_code = status.HTTP_409_CONFLICT
        return response

    # 400 - Validation Error
    if isinstance(exc, ValidationError):
        print("yes got it innn ValidationError")
        error_response["error"]["code"] = "validation_error"
        error_response["error"]["message"] = "Invalid input."
        error_response["error"]["fields"] = response.data
        response.data = error_response
        return response

    # 401 - Unauthenticated
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        error_response["error"]["code"] = "unauthenticated"
        error_response["error"]["message"] = response.data.get(
            "detail", "Authentication required."
        )
        response.data = error_response
        return response

    # 403 - Forbidden
    if response.status_code == status.HTTP_403_FORBIDDEN:
        error_response["error"]["code"] = "forbidden"
        error_response["error"]["message"] = response.data.get(
            "detail", "You do not have permission."
        )
        response.data = error_response
        return response

    # 404 - Not Found
    if response.status_code == status.HTTP_404_NOT_FOUND:
        error_response["error"]["code"] = "not_found"
        error_response["error"]["message"] = response.data.get(
            "detail", "Resource not found."
        )
        response.data = error_response
        return response

    return response


class AlreadyExistsConflictException(APIException):
    status_code = 409
    default_detail = "Conflict occurred."
    default_code = "conflict"
