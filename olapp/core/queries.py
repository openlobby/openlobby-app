from .graphql import (
    NotFoundError,
    call_query,
    encode_global_id,
    decode_global_id,
    pythonize_report,
    pythonize_author,
)


def search_reports(api_url, slice, *, token=None):
    if 'after' in slice:
        slice_info = """(query:"{query}", highlight:true, first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(query:"{query}", highlight:true, first:{first})""".format(**slice)

    query = """
    searchReports {slice} {{
        totalCount
        edges {{
            node {{
                id
                date
                published
                title
                body
                receivedBenefit
                providedBenefit
                ourParticipants
                otherParticipants
                extra
                author {{
                    id
                    firstName
                    lastName
                    hasCollidingName
                    extra
                }}
            }}
        }}
    }}
    """.format(slice=slice_info)
    data, viewer = call_query(api_url, query, token=token)
    search = data['searchReports']

    for edge in search['edges']:
        edge['node'] = pythonize_report(edge['node'])

    return search, viewer


def get_report(api_url, id, *, token=None):
    query = """
    node (id:"{id}") {{
        ... on Report {{
            id
            date
            published
            title
            body
            receivedBenefit
            providedBenefit
            ourParticipants
            otherParticipants
            isDraft
            extra
            author {{
                id
                firstName
                lastName
                hasCollidingName
                extra
            }}
        }}
    }}
    """.format(id=encode_global_id('Report', id))
    data, viewer = call_query(api_url, query, token=token)

    report = data['node']
    if report is None:
        raise NotFoundError()

    return pythonize_report(report), viewer


def get_author_with_reports(api_url, id, slice, *, token=None):
    if 'after' in slice:
        slice_info = """(first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(first:{first})""".format(**slice)

    query = """
    node (id:"{id}") {{
        ... on Author {{
            id
            firstName
            lastName
            hasCollidingName
            extra
            reports {slice} {{
                totalCount
                edges {{
                    node {{
                        id
                        date
                        published
                        title
                        body
                        receivedBenefit
                        providedBenefit
                        ourParticipants
                        otherParticipants
                        extra
                    }}
                }}
            }}
        }}
    }}
    """.format(id=encode_global_id('Author', id), slice=slice_info)
    data, viewer = call_query(api_url, query, token=token)

    author = data['node']
    if author is None:
        raise NotFoundError()

    author = pythonize_author(author)

    for edge in author['reports']['edges']:
        edge['node'] = pythonize_report(edge['node'])
        # extend report with author info
        edge['node']['author'] = {
            'id': author['id'],
            'firstName': author['firstName'],
            'lastName': author['lastName'],
            'hasCollidingName': author['hasCollidingName'],
            'extra': author['extra'],
        }

    return author, viewer


def get_viewer(api_url, *, token=None):
    data, viewer = call_query(api_url, '', token=token)
    return viewer


def get_login_shortcuts(api_url, *, token=None):
    query = """
    loginShortcuts {
        id
        name
    }
    """
    data, viewer = call_query(api_url, query, token=token)
    shortcuts = data['loginShortcuts']
    for shortcut in shortcuts:
        type, id = decode_global_id(shortcut['id'])
        shortcut['id'] = id
    return shortcuts, viewer


def get_authors(api_url, slice, *, token=None):
    if 'after' in slice:
        slice_info = """(first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(first:{first})""".format(**slice)

    query = """
    authors {slice} {{
        totalCount
        edges {{
            node {{
                id
                firstName
                lastName
                hasCollidingName
                totalReports
                extra
            }}
        }}
    }}
    """.format(slice=slice_info)
    data, viewer = call_query(api_url, query, token=token)
    authors = data['authors']

    for edge in authors['edges']:
        edge['node'] = pythonize_author(edge['node'])

    return authors, viewer


def get_report_drafts(api_url, *, token=None):
    query = """
    reportDrafts {
        id
        date
        title
        body
    }
    """
    data, viewer = call_query(api_url, query, token=token)
    drafts = data['reportDrafts']
    for draft in drafts:
        draft = pythonize_report(draft)
    return drafts, viewer
