from functools import wraps
from django.conf import settings


class UnauthorizedError(Exception):
    pass


def get_token(func):
    """View method decorator which gets token from cookie and passes it in
    method kwargs.
    """
    @wraps(func)
    def inner_func(self, *args, **kwargs):
        kwargs['token'] = self.request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE)
        return func(self, *args, **kwargs)
    return inner_func


def viewer_required(func):
    """View method decorator which raises UnauthorizedError if logged in viewer
    is not in context data.
    """
    @wraps(func)
    def inner_func(self, *args, **kwargs):
        context = func(self, *args, **kwargs)
        if context.get('viewer') is None:
            raise UnauthorizedError()
        return context
    return inner_func


def shorten_pages(page, pages, total_pages):
    if total_pages <= 20:
        return pages

    items = [1, total_pages]
    for offset in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]:
        i = page + offset
        if i not in items and 0 < i <= total_pages:
            items.append(i)

    out = []
    last = 0
    for i in sorted(items):
        if i - last > 1:
            out.append(None)
        out.append(pages[i-1])
        last = i

    return out


def get_page_info(page, pages, total_pages):
    if page == 1:
        previous_url = None
    else:
        previous_url = pages[page - 2]['url']

    if page == total_pages or total_pages == 0:
        next_url = None
    else:
        next_url = pages[page]['url']

    return {
        'show': len(pages) > 1,
        'page': page,
        'pages': shorten_pages(page, pages, total_pages),
        'total_pages': total_pages,
        'previous_url': previous_url,
        'next_url': next_url,
    }
