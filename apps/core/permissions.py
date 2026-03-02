from django.core.exceptions import PermissionDenied
from functools import wraps


def is_admin(user):
    return user.is_authenticated and user.role == "ADMIN"


def is_reviewer(user):
    return user.is_authenticated and user.role == "REVIEWER"


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            if request.user.role not in allowed_roles:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
