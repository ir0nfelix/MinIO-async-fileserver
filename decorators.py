from werkzeug import exceptions

import settings
from utils import get_class_by_path


def authenticate(f):
    def decorator(request):
        try:
            authentication_backend = get_class_by_path(settings.AUTHENTICATION_BACKEND)
            authenticator = authentication_backend()
        except Exception:
            raise exceptions.Unauthorized()
        authenticator.authenticate(request)
        return f(request)
    return decorator
