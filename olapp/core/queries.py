import arrow
import requests
import json
import base64


class GraphQLError(Exception):
    pass


class NotFoundError(Exception):
    pass


def post_query(api_url, query, *, variables=None, token=None):
    if token is not None:
        headers = {'Authorization': 'Bearer {}'.format(token)}
    else:
        headers = {}

    payload = {'query': query, 'variables': variables}
    response = requests.post(api_url, json=payload, headers=headers)
    content = response.json()

    if 'errors' in content:
        raise GraphQLError(content['errors'])
    return content['data']


def decode_global_id(global_id):
    type, id = base64.b64decode(global_id).decode('utf-8').split(':')
    return id


def encode_global_id(type, id):
    global_id = '{}:{}'.format(type, id)
    return base64.b64encode(global_id.encode('utf-8')).decode('utf-8')


def encode_cursor(num):
    return base64.b64encode(str(num).encode('utf-8')).decode('utf-8')


def pythonize_user(user):
    user['id'] = decode_global_id(user['id'])
    user['extra'] = json.loads(user['extra'])
    return user


def pythonize_report(report):
    report['id'] = decode_global_id(report['id'])
    report['extra'] = json.loads(report['extra'])
    report['date'] = arrow.get(report['date']).date
    report['published'] = arrow.get(report['published']).datetime
    if 'author' in report:
        report['author'] = pythonize_user(report['author'])
    return report


def get_viewer_from_data(data):
    viewer = data.get('viewer')
    if viewer is None:
        return None
    return pythonize_user(viewer)


VIEWER = """
    viewer {
        id
        name
        email
        openidUid
        extra
    }
"""


def search_reports(api_url, slice, *, token=None, viewer=VIEWER):
    if 'after' in slice:
        slice_info = """(query:"{query}", highlight:true, first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(query:"{query}", highlight:true, first:{first})""".format(**slice)

    query = """
    query {{
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
                    extra
                    author {{
                        id
                        name
                        extra
                    }}
                }}
            }}
        }}
        {viewer}
    }}
    """.format(slice=slice_info, viewer=viewer)
    data = post_query(api_url, query, token=token)
    search = data['searchReports']

    for edge in search['edges']:
        edge['node'] = pythonize_report(edge['node'])

    viewer = get_viewer_from_data(data)
    return search, viewer


def get_report(api_url, id, *, token=None, viewer=VIEWER):
    query = """
    query {{
        node (id:"{id}") {{
            ... on Report {{
                id
                date
                published
                title
                body
                receivedBenefit
                providedBenefit
                extra
                author {{
                    id
                    name
                    extra
                }}
            }}
        }}
        {viewer}
    }}
    """.format(id=encode_global_id('Report', id), viewer=viewer)
    data = post_query(api_url, query, token=token)

    report = data['node']
    if report is None:
        raise NotFoundError()

    viewer = get_viewer_from_data(data)
    return pythonize_report(report), viewer


def get_user(api_url, id, *, token=None, viewer=VIEWER):
    query = """
    query {{
        node (id:"{id}") {{
            ... on User {{
                id
                name
                extra
            }}
        }}
        {viewer}
    }}
    """.format(id=encode_global_id('User', id), viewer=viewer)
    data = post_query(api_url, query, token=token)

    user = data['node']
    if user is None:
        raise NotFoundError()

    viewer = get_viewer_from_data(data)
    return pythonize_user(user), viewer


def get_user_with_reports(api_url, id, slice, *, token=None, viewer=VIEWER):
    if 'after' in slice:
        slice_info = """(first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(first:{first})""".format(**slice)

    query = """
    query {{
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
                            extra
                        }}
                    }}
                }}
            }}
        }}
        {viewer}
    }}
    """.format(id=encode_global_id('User', id), slice=slice_info, viewer=viewer)
    data = post_query(api_url, query, token=token)

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

    viewer = get_viewer_from_data(data)
    return user, viewer


def get_viewer(api_url, *, token=None, viewer=VIEWER):
    query = """
    query {{
        {viewer}
    }}
    """.format(viewer=viewer)
    data = post_query(api_url, query, token=token)

    return get_viewer_from_data(data)
