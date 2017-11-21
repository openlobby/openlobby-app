import requests


class MutationError(Exception):
    pass


def post_mutation(api_url, mutation):
    response = requests.post(api_url, json={'query': mutation})
    content = response.json()
    if 'errors' in content:
        raise MutationError(content['errors'])
    return content['data']


def login(api_url, openid_uid, redirect_uri):
    mutation = """
    mutation {{
        login (input: {{ openidUid: "{openid_uid}", redirectUri: "{redirect_uri}" }}) {{
            authorizationUrl
        }}
    }}
    """.format(openid_uid=openid_uid, redirect_uri=redirect_uri)
    data = post_mutation(api_url, mutation)
    return data['login']


def login_redirect(api_url, query_string):
    mutation = """
    mutation {{
        loginRedirect (input: {{ queryString: "{query_string}" }}) {{
            accessToken
        }}
    }}
    """.format(query_string=query_string)
    data = post_mutation(api_url, mutation)
    return data['loginRedirect']
