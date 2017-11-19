from django.conf.urls import url
from olapp.core.views import IndexView, ReportView, UserView, LoginView, LoginRedirectView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^login-redirect/$', LoginRedirectView.as_view(), name='login-redirect'),
    url(r'^report/(?P<id>[0-9A-Za-z-_]+)/$', ReportView.as_view(), name='report'),
    url(r'^user/(?P<id>[0-9A-Za-z-_]+)/$', UserView.as_view(), name='user'),
    url(r'^user/(?P<id>[0-9A-Za-z-_]+)/(?P<page>[0-9]+)/$', UserView.as_view(), name='user-page'),
]
