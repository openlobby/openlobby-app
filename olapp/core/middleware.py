from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import redirect
from django.urls import reverse

from .graphql import ServiceUnavailableError, InvalidTokenError
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

        if isinstance(exception, InvalidTokenError):
            response = HttpResponseRedirect(reverse('index'))
            response.delete_cookie(settings.ACCESS_TOKEN_COOKIE)
            return response

        return None
