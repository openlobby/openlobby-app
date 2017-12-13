from .graphql import (
    NotFoundError,
    call_query,
    encode_global_id,
    decode_global_id,
    pythonize_report,
    pythonize_user,
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
                    name
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
            extra
            author {{
                id
                name
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


def get_user_with_reports(api_url, id, slice, *, token=None):
    if 'after' in slice:
        slice_info = """(first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(first:{first})""".format(**slice)

    query = """
    node (id:"{id}") {{
        ... on User {{
            id
            name
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
    """.format(id=encode_global_id('User', id), slice=slice_info)
    data, viewer = call_query(api_url, query, token=token)

    user = data['node']
    if user is None:
        raise NotFoundError()

    user = pythonize_user(user)

    for edge in user['reports']['edges']:
        edge['node'] = pythonize_report(edge['node'])
        # extend report with author info
        edge['node']['author'] = {
            'id': user['id'],
            'name': user['name'],
            'extra': user['extra'],
        }

    return user, viewer


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
