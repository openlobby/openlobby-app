from django.conf import settings
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
from .forms import SearchForm, LoginForm
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
            cursor = queries.encode_cursor((page - 1) * REPORTS_PER_PAGE)
            slice = {'query': query, 'first': REPORTS_PER_PAGE, 'after': cursor}
        else:
            slice = {'query': query, 'first': REPORTS_PER_PAGE}

        search = queries.search_reports(settings.OPENLOBBY_API_URL, slice)
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
            context['report'] = queries.get_report(settings.OPENLOBBY_API_URL, kwargs['id'])
        except queries.NotFoundError:
            raise Http404()
        return context


class UserView(TemplateView):
    template_name = 'core/user.html'

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        id = kwargs['id']

        page = int(kwargs.get('page', 1))
        if page > 1:
            cursor = queries.encode_cursor((page - 1) * REPORTS_PER_PAGE)
            slice = {'first': REPORTS_PER_PAGE, 'after': cursor}
        else:
            slice = {'first': REPORTS_PER_PAGE}

        try:
            user = queries.get_user_with_reports(settings.OPENLOBBY_API_URL, id, slice)
        except queries.NotFoundError:
            raise Http404()

        context['user'] = user
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
        token = data['accessToken']
        payload = jwt.decode(token, verify=False)
        max_age = payload['exp'] - time.time()
        response = HttpResponseRedirect(reverse('index'))
        response.set_cookie('access_token', token, max_age=max_age, httponly=True)
        return response
