import requests


def post_mutation(api_url, mutation):
    response = requests.post(api_url, json={'mutation': mutation})
    content = response.json()
    if 'errors' in content:
        raise Exception(content['errors'])
    return content['data']


def login(api_url, openid_uid, redirect_uri):
    pass
