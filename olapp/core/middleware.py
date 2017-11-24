from django.http import HttpResponse
from django.template import loader

from .queries import ServiceUnavailableError


class ServiceUnavailableMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, ServiceUnavailableError):
            return HttpResponse(loader.render_to_string('503.html'), status=503)
        return None
