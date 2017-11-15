import urllib.parse
import math
from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.views.generic.base import TemplateView

from .forms import SearchForm
from .queries import (
    NotFoundError,
    encode_cursor,
    get_report,
    get_author_with_reports,
    search_reports,
)
from .utils import get_page_info


REPORTS_PER_PAGE = 10


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

        try:
            page = int(self.request.GET.get('p', 1))
        except ValueError:
            raise Http404

        if page > 1:
            cursor = encode_cursor((page - 1) * REPORTS_PER_PAGE)
            slice = {'query': query, 'first': REPORTS_PER_PAGE, 'after': cursor}
        else:
            slice = {'query': query, 'first': REPORTS_PER_PAGE}

        search = search_reports(settings.OPENLOBBY_API_URL, slice)
        context['reports'] = [edge['node'] for edge in search['edges']]
        context['total_reports'] = search['totalCount']

        total_pages = math.ceil(search['totalCount'] / REPORTS_PER_PAGE)

        if page > total_pages and page != 1:
            raise Http404

        url = reverse('index')
        pages = []
        for num in range(1, total_pages + 1):
            url_qs = urllib.parse.urlencode({'q': query, 'p': num})
            page_url = '{}?{}'.format(url, url_qs)
            pages.append({'num': num, 'url': page_url, 'active': page == num})

        context['page_info'] = get_page_info(page, pages, total_pages)

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
        id = kwargs['id']

        page = int(kwargs.get('page', 1))
        if page > 1:
            cursor = encode_cursor((page - 1) * REPORTS_PER_PAGE)
            slice = {'first': REPORTS_PER_PAGE, 'after': cursor}
        else:
            slice = {'first': REPORTS_PER_PAGE}

        try:
            author = get_author_with_reports(settings.OPENLOBBY_API_URL, id, slice)
        except NotFoundError:
            raise Http404()

        context['author'] = author
        context['reports'] = [edge['node'] for edge in author['reports']['edges']]
        context['total_reports'] = author['reports']['totalCount']

        total_pages = math.ceil(author['reports']['totalCount'] / REPORTS_PER_PAGE)

        pages = []
        for num in range(1, total_pages + 1):
            if num == 1:
                url = reverse('author', kwargs={'id': id})
            else:
                url = reverse('author-page', kwargs={'id': id, 'page': num})
            pages.append({'num': num, 'url': url, 'active': page == num})

        context['page_info'] = get_page_info(page, pages, total_pages)

        return context
