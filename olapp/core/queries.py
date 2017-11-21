import arrow
import requests
import json
import base64


class NotFoundError(Exception):
    pass


class QueryError(Exception):
    pass


def post_query(api_url, query, *, token=None):
    if token is not None:
        headers = {'Authorization': 'Bearer {}'.format(token)}
    else:
        headers = {}
    response = requests.post(api_url, json={'query': query}, headers=headers)
    content = response.json()
    if 'errors' in content:
        raise QueryError(content['errors'])
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
    report['date'] = arrow.get(report['date'])
    report['published'] = arrow.get(report['published'])
    if 'author' in report:
        report['author'] = pythonize_user(report['author'])
    return report


def search_reports(api_url, slice):
    if 'after' in slice:
        slice_info = """(query:"{query}", first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(query:"{query}", first:{first})""".format(**slice)

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
    }}
    """.format(slice=slice_info)
    data = post_query(api_url, query)
    search = data['searchReports']

    for edge in search['edges']:
        edge['node'] = pythonize_report(edge['node'])

    return search


def get_report(api_url, id):
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
    }}
    """.format(id=encode_global_id('Report', id))
    data = post_query(api_url, query)

    report = data['node']
    if report is None:
        raise NotFoundError()

    return pythonize_report(report)


def get_user(api_url, id):
    query = """
    query {{
        node (id:"{id}") {{
            ... on User {{
                id
                name
                extra
            }}
        }}
    }}
    """.format(id=encode_global_id('User', id))
    data = post_query(api_url, query)

    user = data['node']
    if user is None:
        raise NotFoundError()

    return pythonize_user(user)


def get_user_with_reports(api_url, id, slice):
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
    }}
    """.format(id=encode_global_id('User', id), slice=slice_info)
    data = post_query(api_url, query)

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

    return user


def get_viewer(api_url, *, token=None):
    query = """
    query {
        viewer {
            id
            name
            email
            openidUid
            extra
        }
    }
    """
    data = post_query(api_url, query, token=token)

    user = data['viewer']
    if user is None:
        raise NotFoundError()

    return pythonize_user(user)
