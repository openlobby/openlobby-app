from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
import jwt
import math
import time
import urllib.parse

from . import queries
from . import mutations
from .forms import SearchForm, LoginForm, NewReportForm
from .utils import get_page_info, get_token, viewer_required


REPORTS_PER_PAGE = 10


class IndexView(TemplateView):
    template_name = 'core/index.html'

    @get_token
    def get_context_data(self, token, **kwargs):
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
            raise SuspiciousOperation

        if page > 1:
            cursor = queries.encode_cursor((page - 1) * REPORTS_PER_PAGE)
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


class ReportView(TemplateView):
    template_name = 'core/report.html'

    @get_token
    def get_context_data(self, token, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)

        try:
            report, viewer = queries.get_report(settings.OPENLOBBY_API_URL, kwargs['id'], token=token)
        except queries.NotFoundError:
            raise Http404

        context['report'] = report
        context['viewer'] = viewer
        return context


class UserView(TemplateView):
    template_name = 'core/user.html'

    @get_token
    def get_context_data(self, token, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        id = kwargs['id']

        page = int(kwargs.get('page', 1))
        if page > 1:
            cursor = queries.encode_cursor((page - 1) * REPORTS_PER_PAGE)
            slice = {'first': REPORTS_PER_PAGE, 'after': cursor}
        else:
            slice = {'first': REPORTS_PER_PAGE}

        try:
            user, viewer = queries.get_user_with_reports(settings.OPENLOBBY_API_URL, id, slice, token=token)
        except queries.NotFoundError:
            raise Http404

        context['user'] = user
        context['viewer'] = viewer
        context['reports'] = [edge['node'] for edge in user['reports']['edges']]
        context['total_reports'] = user['reports']['totalCount']

        total_pages = math.ceil(user['reports']['totalCount'] / REPORTS_PER_PAGE)

        pages = []
        for num in range(1, total_pages + 1):
            if num == 1:
                url = reverse('user', kwargs={'id': id})
            else:
                url = reverse('user-page', kwargs={'id': id, 'page': num})
            pages.append({'num': num, 'url': url, 'active': page == num})

        context['page_info'] = get_page_info(page, pages, total_pages)

        return context


class LoginView(FormView):
    template_name = 'core/login.html'
    form_class = LoginForm

    def get_success_url(self):
        return self.authorization_url

    def form_valid(self, form):
        openid_uid = form.cleaned_data['openid_uid']
        redirect_uri = urllib.parse.urljoin(settings.APP_URL, reverse('login-redirect'))
        data = mutations.login(settings.OPENLOBBY_API_URL, openid_uid, redirect_uri)
        self.authorization_url = data['authorizationUrl']
        return super(LoginView, self).form_valid(form)


class LoginRedirectView(View):

    def get(self, request):
        query_string = request.META['QUERY_STRING']
        data = mutations.login_redirect(settings.OPENLOBBY_API_URL, query_string)

        # get cookie max_age from token
        token = data['accessToken']
        payload = jwt.decode(token, verify=False)
        max_age = payload['exp'] - time.time()

        response = HttpResponseRedirect(reverse('account'))
        response.set_cookie(settings.ACCESS_TOKEN_COOKIE, token, max_age=max_age)
        return response


class LogoutView(View):

    @get_token
    def get(self, request, token):
        success = mutations.logout(settings.OPENLOBBY_API_URL, token=token)
        if success:
            response = HttpResponseRedirect(reverse('index'))
            response.delete_cookie(settings.ACCESS_TOKEN_COOKIE)
        else:
            response = HttpResponseRedirect(reverse('account'))
        return response


class AccountView(TemplateView):
    template_name = 'core/account.html'

    @viewer_required
    @get_token
    def get_context_data(self, token, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['viewer'] = queries.get_viewer(settings.OPENLOBBY_API_URL, token=token)
        return context


class NewReportView(FormView):
    template_name = 'core/new_report.html'
    form_class = NewReportForm

    def get_success_url(self):
        return reverse('new-report-success')

    @get_token
    def form_valid(self, form, token):
        mutations.new_report(settings.OPENLOBBY_API_URL, form.cleaned_data, token=token)
        return super(NewReportView, self).form_valid(form)

    @viewer_required
    @get_token
    def get_context_data(self, token, **kwargs):
        self.viewer = queries.get_viewer(settings.OPENLOBBY_API_URL, token=token)
        context = super(NewReportView, self).get_context_data(**kwargs)
        context['viewer'] = self.viewer
        return context

    def get_initial(self):
        data = super(NewReportView, self).get_initial()
        if hasattr(self, 'viewer') and self.viewer is not None:
            data['our_participants'] = self.viewer['name']
        return data


class NewReportSuccessView(TemplateView):
    template_name = 'core/new_report_success.html'

    @get_token
    def get_context_data(self, token, **kwargs):
        context = super(NewReportSuccessView, self).get_context_data(**kwargs)
        context['viewer'] = queries.get_viewer(settings.OPENLOBBY_API_URL, token=token)
        return context
