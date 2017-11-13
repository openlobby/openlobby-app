from django.conf import settings
from django.http import Http404
from django.views.generic.base import TemplateView

from .forms import SearchForm
from .queries import NotFoundError, search_reports, get_report, get_author


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        query = ''

        form = SearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            # replace form with new one with cleaned input
            form = SearchForm({'q': query})

        context['form'] = form
        context['reports'] = search_reports(settings.OPENLOBBY_API_URL, query)
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
