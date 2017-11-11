from django.conf import settings
from django.http import Http404
from django.views.generic.base import TemplateView

from .queries import NotFoundError, get_all_reports, get_report, get_author


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['reports'] = get_all_reports(settings.OPENLOBBY_API_URL)
        return context


class ReportView(TemplateView):
    template_name = 'core/report.html'

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        try:
            context['report'] = get_report(settings.OPENLOBBY_API_URL, kwargs['id'])
        except NotFoundError:
            raise Http404()
        return context


class AuthorView(TemplateView):
    template_name = 'core/author.html'

    def get_context_data(self, **kwargs):
        context = super(AuthorView, self).get_context_data(**kwargs)
        try:
            context['author'] = get_author(settings.OPENLOBBY_API_URL, kwargs['id'])
        except NotFoundError:
            raise Http404()
        return context
