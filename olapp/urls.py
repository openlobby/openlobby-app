from django.conf.urls import url
from olapp.core.views import (
    AboutView,
    AccountView,
    AuthorView,
    AuthorsView,
    EditReportView,
    NewReportView,
    IndexView,
    LoginView,
    LoginByShortcutView,
    LoginRedirectView,
    LogoutView,
    ReportView,
    ReportHistoryView,
)

urlpatterns = [
    url(r"^$", IndexView.as_view(), name="index"),
    url(r"^login/$", LoginView.as_view(), name="login"),
    url(
        r"^login/(?P<shortcut_id>[0-9A-Za-z-_]+)/$",
        LoginByShortcutView.as_view(),
        name="login-by-shortcut",
    ),
    url(r"^login-redirect/$", LoginRedirectView.as_view(), name="login-redirect"),
    url(r"^logout/$", LogoutView.as_view(), name="logout"),
    url(r"^about/$", AboutView.as_view(), name="about"),
    url(r"^account/$", AccountView.as_view(), name="account"),
    url(r"^new-report/$", NewReportView.as_view(), name="new-report"),
    url(r"^report/(?P<id>[0-9A-Za-z-_]+)/$", ReportView.as_view(), name="report"),
    url(
        r"^report/(?P<id>[0-9A-Za-z-_]+)/edit/$",
        EditReportView.as_view(),
        name="edit-report",
    ),
    url(
        r"^report/(?P<id>[0-9A-Za-z-_]+)/history/$",
        ReportHistoryView.as_view(),
        name="report-history",
    ),
    url(r"^authors/$", AuthorsView.as_view(), name="authors"),
    url(r"^author/(?P<id>[0-9A-Za-z-_]+)/$", AuthorView.as_view(), name="author"),
    url(
        r"^author/(?P<id>[0-9A-Za-z-_]+)/(?P<page>[0-9]+)/$",
        AuthorView.as_view(),
        name="author-page",
    ),
]
