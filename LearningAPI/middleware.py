# middleware.py
import uuid
import structlog
from django.utils.deprecation import MiddlewareMixin

log = structlog.get_logger(__name__)

class RequestContextMiddleware(MiddlewareMixin):
    """
    Middleware to attach request-scoped context like request_id, path, and method.
    """
    def process_request(self, request):
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.path,
            method=request.method,
        )
        log.debug(
            "RequestContextMiddleware: request context bound",
            request_id=request_id,
            path=request.path,
            method=request.method,
        )

    def process_response(self, request, response):
        structlog.contextvars.clear_contextvars()
        return response

    def process_exception(self, request, exception):
        structlog.contextvars.clear_contextvars()
        log.exception("RequestContextMiddleware: exception occurred", exc_info=exception)
