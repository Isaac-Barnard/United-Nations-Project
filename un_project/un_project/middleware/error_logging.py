import logging
import traceback

logger = logging.getLogger(__name__)

class ExceptionLogger:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(
                f"Unhandled exception\n"
                f"Path: {request.path}\n"
                f"Method: {request.method}\n"
                f"User: {getattr(request, 'user', None)}\n"
                f"GET: {request.GET.dict()}\n"
                f"POST: {request.POST.dict()}\n"
                f"Exception: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}",
                exc_info=True
            )
            raise