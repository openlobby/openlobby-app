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


def parse_dates(reports):
    for r in reports:
        r['date'] = arrow.get(r['date'])
        r['published'] = arrow.get(r['published'])
    return reports


def parse_extra(reports):
    for r in reports:
        r['extra'] = json.loads(r['extra'])
        r['author']['extra'] = json.loads(r['author']['extra'])
    return reports


def parse_global_ids(reports):
    for r in reports:
        r['id'] = decode_global_id(r['id'])
        r['author']['id'] = decode_global_id(r['author']['id'])
    return reports


def get_all_reports(api_url):
    query = """
    query {
        reports {
            id
            date
            published
            title
            body
            receivedBenefit
            providedBenefit
            extra
            author {
                id
                name
                extra
            }
        }
    }
    """
    data = post_query(api_url, query)
    reports = data['reports']
    reports = parse_global_ids(reports)
    reports = parse_dates(reports)
    reports = parse_extra(reports)
    return reports


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
    reports = parse_global_ids([report])
    reports = parse_dates(reports)
    reports = parse_extra(reports)
    return reports[0]


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
    author['id'] = decode_global_id(author['id'])
    author['extra'] = json.loads(author['extra'])
    return author
