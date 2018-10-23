from .graphql import call_mutation, encode_global_id, decode_global_id


def login(api_url, openid_uid, redirect_uri):
    mutation = f"""
    mutation {{
        login (input: {{ openidUid: "{openid_uid}", redirectUri: "{redirect_uri}" }}) {{
            authorizationUrl
        }}
    }}
    """
    data = call_mutation(api_url, mutation)
    return data["login"]


def login_by_shortcut(api_url, shortcut_id, redirect_uri):
    mutation = f"""
    mutation {{
        loginByShortcut (input: {{ shortcutId: "{shortcut_id}", redirectUri: "{redirect_uri}" }}) {{
            authorizationUrl
        }}
    }}
    """
    data = call_mutation(api_url, mutation)
    return data["loginByShortcut"]


def logout(api_url, *, token=None):
    mutation = """
    mutation {
        logout (input: {}) {
            success
        }
    }
    """
    data = call_mutation(api_url, mutation, token=token)
    return data["logout"]["success"]


def _date_to_iso_noon(date):
    return f"{date.isoformat()}T12:00:00Z"


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
        "title": report["title"],
        "body": report["body"],
        "receivedBenefit": report["received_benefit"],
        "providedBenefit": report["provided_benefit"],
        "date": _date_to_iso_noon(report["date"]),
        "ourParticipants": report["our_participants"],
        "otherParticipants": report["other_participants"],
        "isDraft": report["is_draft"],
    }
    variables = {"input": input}
    data = call_mutation(api_url, mutation, variables=variables, token=token)
    type, id = decode_global_id(data["createReport"]["report"]["id"])
    return id


def update_report(api_url, report, *, token=None):
    mutation = """
    mutation updateReport ($input: UpdateReportInput!) {
        updateReport (input: $input) {
            report {
                id
            }
        }
    }
    """
    input = {
        "id": encode_global_id("Report", report["id"]),
        "title": report["title"],
        "body": report["body"],
        "receivedBenefit": report["received_benefit"],
        "providedBenefit": report["provided_benefit"],
        "date": _date_to_iso_noon(report["date"]),
        "ourParticipants": report["our_participants"],
        "otherParticipants": report["other_participants"],
        "isDraft": report["is_draft"],
    }
    variables = {"input": input}
    data = call_mutation(api_url, mutation, variables=variables, token=token)
    type, id = decode_global_id(data["updateReport"]["report"]["id"])
    return id
