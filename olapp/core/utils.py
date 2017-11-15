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