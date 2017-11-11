import arrow
import requests
import json


class NotFoundError(Exception):
    pass


def post_query(api_url, query):
    response = requests.post(api_url, json={'query': query})
    content = response.json()
    if 'errors' in content:
        raise Exception(content['errors'])
    return content['data']


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
    """.format(id=id)
    data = post_query(api_url, query)
    report = data['node']
    if report is None:
        raise NotFoundError()
    reports = parse_dates([report])
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
    """.format(id=id)
    data = post_query(api_url, query)
    author = data['node']
    if author is None:
        raise NotFoundError()
    author['extra'] = json.loads(author['extra'])
    return author
