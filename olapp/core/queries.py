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


def search_reports(api_url, search_query):
    query = """
    query {{
        reports (query:"{query}") {{
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
    """.format(query=search_query)
    data = post_query(api_url, query)
    reports = data['reports']
    return [pythonize_report(r) for r in reports]


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
