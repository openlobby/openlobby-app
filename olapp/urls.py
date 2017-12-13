from django.conf.urls import url
from olapp.core.views import (
    AccountView,
    NewReportView,
    NewReportSuccessView,
    IndexView,
    LoginView,
    LoginByShortcutView,
    LoginRedirectView,
    LogoutView,
    ReportView,
    UserView,
)

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^login/(?P<shortcut_id>[0-9A-Za-z-_]+)/$', LoginByShortcutView.as_view(), name='login-by-shortcut'),
    url(r'^login-redirect/$', LoginRedirectView.as_view(), name='login-redirect'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^account/$', AccountView.as_view(), name='account'),
    url(r'^new-report/$', NewReportView.as_view(), name='new-report'),
    url(r'^new-report/success/$', NewReportSuccessView.as_view(), name='new-report-success'),
    url(r'^report/(?P<id>[0-9A-Za-z-_]+)/$', ReportView.as_view(), name='report'),
    url(r'^user/(?P<id>[0-9A-Za-z-_]+)/$', UserView.as_view(), name='user'),
    url(r'^user/(?P<id>[0-9A-Za-z-_]+)/(?P<page>[0-9]+)/$', UserView.as_view(), name='user-page'),
]
