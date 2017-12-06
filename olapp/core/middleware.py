from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

from .graphql import ServiceUnavailableError
from .utils import UnauthorizedError


class CustomErrorResponsesMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, ServiceUnavailableError):
            return HttpResponse(loader.render_to_string('503.html'), status=503)

        if isinstance(exception, UnauthorizedError):
            return redirect('login')

        return None
