import arrow
import base64
import json
import requests
from django.conf import settings


VIEWER = """
    viewer {
        id
        firstName
        lastName
        hasCollidingName
        email
        openidUid
        isAuthor
        extra
    }
"""


class ServiceUnavailableError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class GraphQLError(Exception):
    pass


class NotFoundError(Exception):
    pass


def decode_global_id(global_id):
    return base64.b64decode(global_id).decode('utf-8').split(':')


def encode_global_id(type, id):
    global_id = '{}:{}'.format(type, id)
    return base64.b64encode(global_id.encode('utf-8')).decode('utf-8')


def encode_cursor(num):
    return base64.b64encode(str(num).encode('utf-8')).decode('utf-8')


def pythonize_user(user):
    type, id = decode_global_id(user['id'])
    user['id'] = id
    if user['extra'] is not None:
        user['extra'] = json.loads(user['extra'])
    return user


def pythonize_author(author):
    return pythonize_user(author)


def pythonize_report(report):
    type, id = decode_global_id(report['id'])
    report['id'] = id
    if 'extra' in report and report['extra'] is not None:
        report['extra'] = json.loads(report['extra'])
    if 'date' in report:
        report['date'] = arrow.get(report['date']).to(settings.TIME_ZONE).date()
    if 'published' in report:
        report['published'] = arrow.get(report['published']).to(settings.TIME_ZONE).datetime
    if 'author' in report and report['author'] is not None:
        report['author'] = pythonize_author(report['author'])
    return report


def get_viewer_from_data(data):
    viewer = data.get('viewer')
    if viewer is None:
        return None
    return pythonize_user(viewer)


def call_api(api_url, query, *, variables=None, token=None):
    if token is not None:
        headers = {'Authorization': 'Bearer {}'.format(token)}
    else:
        headers = {}

    payload = {'query': query, 'variables': variables}

    try:
        response = requests.post(api_url, json=payload, headers=headers)
    except requests.exceptions.RequestException:
        raise ServiceUnavailableError

    # unauthorized? it's wrong token
    if response.status_code == 401:
        raise InvalidTokenError()

    content = response.json()

    if 'errors' in content:
        raise GraphQLError(content['errors'])

    return content['data']


def call_query(api_url, query, *, viewer=VIEWER, variables=None, token=None):
    query_ = """
query {{
    {query}
    {viewer}
}}""".format(query=query, viewer=viewer)
    data = call_api(api_url, query_, variables=variables, token=token)
    viewer = get_viewer_from_data(data)
    return data, viewer


def call_mutation(api_url, mutation, *, variables=None, token=None):
    data = call_api(api_url, mutation, variables=variables, token=token)
    return data
