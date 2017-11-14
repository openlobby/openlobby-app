from django.conf.urls import url
from olapp.core.views import IndexView, ReportView, AuthorView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^report/(?P<id>[0-9A-Za-z-_]+)/$', ReportView.as_view(), name='report'),
    url(r'^author/(?P<id>[0-9A-Za-z-_]+)/$', AuthorView.as_view(), name='author'),
    url(r'^author/(?P<id>[0-9A-Za-z-_]+)/(?P<page>[0-9]+)/$', AuthorView.as_view(), name='author-page'),
]
