import structlog
import uuid
from django.utils.deprecation import MiddlewareMixin

log = structlog.get_logger(__name__)

class RequestContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request_id = str(uuid.uuid4())
        user_id = getattr(request.user, 'id', 'anonymous') # Get user ID if authenticated

        log.debug("RequestContextMiddleware processing request",
                  user_authenticated=request.user.is_authenticated,
                  user_id_from_request=user_id,
                  request_path=request.path)

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            user_id=user_id,
            path=request.path,
            method=request.method,
        )

    def process_response(self, request, response):
        structlog.contextvars.clear_contextvars()
        return response

    def process_exception(self, request, exception):
        structlog.contextvars.clear_contextvars()