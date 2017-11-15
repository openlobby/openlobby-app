import arrow
import requests
import json
import base64


class NotFoundError(Exception):
    pass


def post_query(api_url, query):
    response = requests.post(api_url, json={'query': query})
    content = response.json()
    if 'errors' in content:
        raise Exception(content['errors'])
    return content['data']


def decode_global_id(global_id):
    type, id = base64.b64decode(global_id).decode('utf-8').split(':')
    return id


def encode_global_id(type, id):
    global_id = '{}:{}'.format(type, id)
    return base64.b64encode(global_id.encode('utf-8')).decode('utf-8')


def encode_cursor(num):
    return base64.b64encode(str(num).encode('utf-8')).decode('utf-8')


def pythonize_author(author):
    author['id'] = decode_global_id(author['id'])
    author['extra'] = json.loads(author['extra'])
    return author


def pythonize_report(report):
    report['id'] = decode_global_id(report['id'])
    report['extra'] = json.loads(report['extra'])
    report['date'] = arrow.get(report['date'])
    report['published'] = arrow.get(report['published'])
    if 'author' in report:
        report['author'] = pythonize_author(report['author'])
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


def get_author(api_url, id):
    query = """
    query {{
        node (id:"{id}") {{
            ... on Author {{
                id
                name
                extra
            }}
        }}
    }}
    """.format(id=encode_global_id('Author', id))
    data = post_query(api_url, query)

    author = data['node']
    if author is None:
        raise NotFoundError()

    return pythonize_author(author)


def get_author_with_reports(api_url, id, slice):
    if 'after' in slice:
        slice_info = """(first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(first:{first})""".format(**slice)

    query = """
    query {{
        node (id:"{id}") {{
            ... on Author {{
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
    """.format(id=encode_global_id('Author', id), slice=slice_info)
    data = post_query(api_url, query)

    author = data['node']
    if author is None:
        raise NotFoundError()

    author = pythonize_author(author)

    for edge in author['reports']['edges']:
        edge['node'] = pythonize_report(edge['node'])
        # extend report with author info
        edge['node']['author'] = {
            'id': author['id'],
            'name': author['name'],
            'extra': author['extra'],
        }

    return author
