from .graphql import call_mutation


def login(api_url, openid_uid, redirect_uri):
    mutation = """
    mutation {{
        login (input: {{ openidUid: "{openid_uid}", redirectUri: "{redirect_uri}" }}) {{
            authorizationUrl
        }}
    }}
    """.format(openid_uid=openid_uid, redirect_uri=redirect_uri)
    data = call_mutation(api_url, mutation)
    return data['login']


def login_by_shortcut(api_url, shortcut_id, redirect_uri):
    mutation = """
    mutation {{
        loginByShortcut (input: {{ shortcutId: "{shortcut_id}", redirectUri: "{redirect_uri}" }}) {{
            authorizationUrl
        }}
    }}
    """.format(shortcut_id=shortcut_id, redirect_uri=redirect_uri)
    data = call_mutation(api_url, mutation)
    return data['loginByShortcut']


def logout(api_url, *, token=None):
    mutation = """
    mutation {
        logout (input: {}) {
            success
        }
    }
    """
    data = call_mutation(api_url, mutation, token=token)
    return data['logout']['success']


def create_report(api_url, report, *, token=None):
    mutation = """
    mutation createReport ($input: CreateReportInput!) {
        createReport (input: $input) {
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
    data = call_mutation(api_url, mutation, variables=variables, token=token)
    return data['createReport']['report']
