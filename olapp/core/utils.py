def get_page_info(page, pages, total_pages):
    if page == 1:
        previous_url = None
    else:
        previous_url = pages[page - 2]['url']

    if page == total_pages:
        next_url = None
    else:
        next_url = pages[page]['url']

    return {
        'show': len(pages) > 1,
        'page': page,
        'pages': pages,
        'total_pages': total_pages,
        'previous_url': previous_url,
        'next_url': next_url,
    }
