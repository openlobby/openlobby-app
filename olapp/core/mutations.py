from .queries import post_query


def login(api_url, openid_uid, redirect_uri):
    mutation = """
    mutation {{
        login (input: {{ openidUid: "{openid_uid}", redirectUri: "{redirect_uri}" }}) {{
            authorizationUrl
        }}
    }}
    """.format(openid_uid=openid_uid, redirect_uri=redirect_uri)
    data = post_query(api_url, mutation)
    return data['login']


def login_redirect(api_url, query_string):
    mutation = """
    mutation {{
        loginRedirect (input: {{ queryString: "{query_string}" }}) {{
            accessToken
        }}
    }}
    """.format(query_string=query_string)
    data = post_query(api_url, mutation)
    return data['loginRedirect']


def logout(api_url, *, token=None):
    mutation = """
    mutation {
        logout (input: {}) {
            success
        }
    }
    """
    data = post_query(api_url, mutation, token=token)
    return data['logout']['success']


def new_report(api_url, report, *, token=None):
    mutation = """
    mutation newReport ($input: NewReportInput!) {
        newReport (input: $input) {
            report {
                id
            }
        }
    }
    """
    input = {
        'title': report['title'],
        'body': report['body'],
        'receivedBenefit': report['received_benefit'],
        'providedBenefit': report['provided_benefit'],
        'date': report['date'].isoformat(),
        'ourParticipants': report['our_participants'],
        'otherParticipants': report['other_participants'],
    }
    variables = {'input': input}
    data = post_query(api_url, mutation, variables=variables, token=token)
    return data['newReport']['report']
