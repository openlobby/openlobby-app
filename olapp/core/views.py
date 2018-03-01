from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
import jwt
import math
import time
import urllib.parse

from . import queries
from . import graphql
from . import mutations
from .forms import SearchForm, LoginForm, ReportForm
from .utils import get_page_info, get_token, viewer_required


AUTHORS_PER_PAGE = 50
REPORTS_PER_PAGE = 10


class IndexView(TemplateView):
    template_name = 'core/index.html'

    @get_token
    def get_context_data(self, token, **kwargs):
        context = super().get_context_data(**kwargs)
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
            raise SuspiciousOperation

        if page > 1:
            cursor = graphql.encode_cursor((page - 1) * REPORTS_PER_PAGE)
            slice = {'query': query, 'first': REPORTS_PER_PAGE, 'after': cursor}
        else:
            slice = {'query': query, 'first': REPORTS_PER_PAGE}

        search, viewer = queries.search_reports(settings.OPENLOBBY_API_URL, slice, token=token)

        context['viewer'] = viewer
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


class AuthorsView(TemplateView):
    template_name = 'core/authors.html'

    @get_token
    def get_context_data(self, token, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            page = int(self.request.GET.get('p', 1))
        except ValueError:
            raise SuspiciousOperation

        if page > 1:
            cursor = graphql.encode_cursor((page - 1) * AUTHORS_PER_PAGE)
            slice = {'first': AUTHORS_PER_PAGE, 'after': cursor}
        else:
            slice = {'first': AUTHORS_PER_PAGE}

        authors, viewer = queries.get_authors(settings.OPENLOBBY_API_URL, slice, token=token)

        context['viewer'] = viewer
        context['authors'] = [edge['node'] for edge in authors['edges']]
        context['total_reports'] = authors['totalCount']

        total_pages = math.ceil(authors['totalCount'] / AUTHORS_PER_PAGE)

        if page > total_pages and page != 1:
            raise Http404

        url = reverse('authors')
        pages = []
        for num in range(1, total_pages + 1):
            url_qs = urllib.parse.urlencode({'p': num})
            page_url = '{}?{}'.format(url, url_qs)
            pages.append({'num': num, 'url': page_url, 'active': page == num})

        context['page_info'] = get_page_info(page, pages, total_pages)

        return context


class ReportView(TemplateView):
    template_name = 'core/report.html'

    @get_token
    def get_context_data(self, token, **kwargs):
        context = super().get_context_data(**kwargs)

        saved = self.request.GET.get('saved')
        if saved is not None:
            context['saved_message'] = True

        try:
            report, viewer = queries.get_report(settings.OPENLOBBY_API_URL, kwargs['id'], token=token)
        except queries.NotFoundError:
            raise Http404

        context['report'] = report
        context['viewer'] = viewer
        return context


class AuthorView(TemplateView):
    template_name = 'core/author.html'

    @get_token
    def get_context_data(self, token, **kwargs):
        context = super().get_context_data(**kwargs)
        id = kwargs['id']

        page = int(kwargs.get('page', 1))
        if page > 1:
            cursor = graphql.encode_cursor((page - 1) * REPORTS_PER_PAGE)
            slice = {'first': REPORTS_PER_PAGE, 'after': cursor}
        else:
            slice = {'first': REPORTS_PER_PAGE}

        try:
            author, viewer = queries.get_author_with_reports(settings.OPENLOBBY_API_URL, id, slice, token=token)
        except queries.NotFoundError:
            raise Http404

        context['author'] = author
        context['viewer'] = viewer
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


class LoginView(FormView):
    template_name = 'core/login.html'
    form_class = LoginForm

    def get_success_url(self):
        return self.authorization_url

    @get_token
    def get_context_data(self, token, **kwargs):
        context = super().get_context_data(**kwargs)
        login_shortcuts, viewer = queries.get_login_shortcuts(settings.OPENLOBBY_API_URL, token=token)
        context['login_shortcuts'] = login_shortcuts
        context['viewer'] = viewer
        return context

    def form_valid(self, form):
        openid_uid = form.cleaned_data['openid_uid']
        redirect_uri = urllib.parse.urljoin(settings.APP_URL, reverse('login-redirect'))
        data = mutations.login(settings.OPENLOBBY_API_URL, openid_uid, redirect_uri)
        self.authorization_url = data['authorizationUrl']
        return super().form_valid(form)


class LoginByShortcutView(View):

    def get(self, request, **kwargs):
        shortcut_id = graphql.encode_global_id('LoginShortcut', kwargs['shortcut_id'])
        redirect_uri = urllib.parse.urljoin(settings.APP_URL, reverse('login-redirect'))
        data = mutations.login_by_shortcut(settings.OPENLOBBY_API_URL, shortcut_id, redirect_uri)
        return redirect(data['authorizationUrl'])


class LoginRedirectView(View):

    def get(self, request):
        token = request.GET.get('token')

        # get cookie max_age from token
        payload = jwt.decode(token, verify=False)
        max_age = payload['exp'] - time.time()

        response = HttpResponseRedirect(reverse('account'))
        response.set_cookie(settings.ACCESS_TOKEN_COOKIE, token, max_age=max_age)
        return response


class LogoutView(View):

    @get_token
    def get(self, request, token):
        # TODO
        # success = mutations.logout(settings.OPENLOBBY_API_URL, token=token)
        success = True
        if success:
            response = HttpResponseRedirect(reverse('index'))
            response.delete_cookie(settings.ACCESS_TOKEN_COOKIE)
        else:
            response = redirect('account')
        return response


class AccountView(TemplateView):
    template_name = 'core/account.html'

    @viewer_required
    @get_token
    def get_context_data(self, token, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewer'] = queries.get_viewer(settings.OPENLOBBY_API_URL, token=token)
        return context


class NewReportView(FormView):
    template_name = 'core/new_report.html'
    form_class = ReportForm

    def get_success_url(self):
        if self.is_draft:
            url = reverse('edit-report', kwargs={'id': self.id})
        else:
            url = reverse('report', kwargs={'id': self.id})
        return '{}?saved=true'.format(url)

    @get_token
    def form_valid(self, form, token):
        id = mutations.create_report(settings.OPENLOBBY_API_URL, form.cleaned_data, token=token)
        self.id = id
        self.is_draft = form.cleaned_data['is_draft']
        return super().form_valid(form)

    @viewer_required
    @get_token
    def get_context_data(self, token, **kwargs):
        drafts, viewer = queries.get_report_drafts(settings.OPENLOBBY_API_URL, token=token)
        self.viewer = viewer
        context = super().get_context_data(**kwargs)
        context['drafts'] = drafts
        context['viewer'] = self.viewer
        return context

    def get_initial(self):
        data = super().get_initial()
        if hasattr(self, 'viewer') and self.viewer is not None:
            data['our_participants'] = '{firstName} {lastName}'.format(**self.viewer)
        return data


class EditReportView(FormView):
    template_name = 'core/edit_report.html'
    form_class = ReportForm

    def get_success_url(self):
        if self.is_draft:
            url = reverse('edit-report', kwargs={'id': self.id})
        else:
            url = reverse('report', kwargs={'id': self.id})
        return '{}?saved=true'.format(url)

    @get_token
    def form_valid(self, form, token):
        id = mutations.update_report(settings.OPENLOBBY_API_URL, form.cleaned_data, token=token)
        self.id = id
        self.is_draft = form.cleaned_data['is_draft']
        return super().form_valid(form)

    @viewer_required
    @get_token
    def get_context_data(self, token, **kwargs):
        id = self.kwargs['id']
        report, viewer = queries.get_report(settings.OPENLOBBY_API_URL, id, token=token)

        if not report['isDraft']:
            if report['author']['id'] != viewer['id']:
                raise Http404

        self.report = report
        self.viewer = viewer

        context = super().get_context_data(**kwargs)

        saved = self.request.GET.get('saved')
        if saved is not None:
            context['saved_message'] = True

        context['report'] = self.report
        context['viewer'] = self.viewer
        return context

    def get_initial(self):
        data = super().get_initial()
        if hasattr(self, 'report') and self.report is not None:
            data['id'] = self.report['id']
            data['date'] = self.report['date']
            data['published'] = self.report['published']
            data['title'] = self.report['title']
            data['body'] = self.report['body']
            data['received_benefit'] = self.report['receivedBenefit']
            data['provided_benefit'] = self.report['providedBenefit']
            data['our_participants'] = self.report['ourParticipants']
            data['other_participants'] = self.report['otherParticipants']
        return data
