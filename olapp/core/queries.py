from enum import Enum

from .graphql import (
    NotFoundError,
    call_query,
    encode_global_id,
    decode_global_id,
    pythonize_report,
    pythonize_author,
    str_argument,
    encode_arguments,
)


report_fields = """
id
date
published
edited
title
body
receivedBenefit
providedBenefit
ourParticipants
otherParticipants
extra
hasRevisions
"""

author_fields = """
id
firstName
lastName
hasCollidingName
extra
"""

revisions_snippet = f"""
revisions {{
    {report_fields}
}}
"""


class AuthorsSort(Enum):
    LAST_NAME = "last-name"
    LAST_NAME_REVERSED = "-last-name"
    TOTAL_REPORTS = "total-reports"


def search_reports(api_url, params, *, token=None):
    arguments = {
        "query": str_argument(params["query"]),
        "first": params["first"],
        "highlight": "true",
    }

    if "after" in params:
        arguments["after"] = str_argument(params["after"])

    arguments = encode_arguments(arguments)

    query = f"""
    searchReports ({arguments}) {{
        totalCount
        edges {{
            node {{
                {report_fields}
                author {{
                    {author_fields}
                }}
            }}
        }}
    }}
    """
    data, viewer = call_query(api_url, query, token=token)
    search = data["searchReports"]

    for edge in search["edges"]:
        edge["node"] = pythonize_report(edge["node"])

    return search, viewer


def get_report(api_url, id, *, token=None, with_revisions=False):
    global_id = encode_global_id("Report", id)
    revisions = revisions_snippet if with_revisions else ""
    query = f"""
    node (id:"{global_id}") {{
        ... on Report {{
            {report_fields}
            isDraft
            author {{
                {author_fields}
            }}
            {revisions}
        }}
    }}
    """
    data, viewer = call_query(api_url, query, token=token)

    report = data["node"]
    if report is None:
        raise NotFoundError()

    report = pythonize_report(report)

    # extend revisions with author info
    if "revisions" in report:
        for revision in report["revisions"]:
            revision["author"] = report["author"]

    return report, viewer


def get_author_with_reports(api_url, id, params, *, token=None):
    arguments = {"first": params["first"]}

    if "after" in params:
        arguments["after"] = str_argument(params["after"])

    arguments = encode_arguments(arguments)

    global_id = encode_global_id("Author", id)
    query = f"""
    node (id:"{global_id}") {{
        ... on Author {{
            {author_fields}
            reports ({arguments}) {{
                totalCount
                edges {{
                    node {{
                        {report_fields}
                    }}
                }}
            }}
        }}
    }}
    """
    data, viewer = call_query(api_url, query, token=token)

    author = data["node"]
    if author is None:
        raise NotFoundError()

    author = pythonize_author(author)

    for edge in author["reports"]["edges"]:
        edge["node"] = pythonize_report(edge["node"])
        # extend report with author info
        edge["node"]["author"] = {
            "id": author["id"],
            "firstName": author["firstName"],
            "lastName": author["lastName"],
            "hasCollidingName": author["hasCollidingName"],
            "extra": author["extra"],
        }

    return author, viewer


def get_viewer(api_url, *, token=None):
    data, viewer = call_query(api_url, "", token=token)
    return viewer


def get_login_shortcuts(api_url, *, token=None):
    query = """
    loginShortcuts {
        id
        name
    }
    """
    data, viewer = call_query(api_url, query, token=token)
    shortcuts = data["loginShortcuts"]
    for shortcut in shortcuts:
        type, id = decode_global_id(shortcut["id"])
        shortcut["id"] = id
    return shortcuts, viewer


def get_authors(api_url, params, *, token=None):
    arguments = {"first": params["first"]}

    if "after" in params:
        arguments["after"] = str_argument(params["after"])

    if params["sort"] == AuthorsSort.LAST_NAME_REVERSED:
        arguments["sort"] = "LAST_NAME"
        arguments["reversed"] = "true"
    elif params["sort"] == AuthorsSort.TOTAL_REPORTS:
        arguments["sort"] = "TOTAL_REPORTS"
    else:
        arguments["sort"] = "LAST_NAME"

    arguments = encode_arguments(arguments)

    query = f"""
    authors ({arguments}) {{
        totalCount
        edges {{
            node {{
                {author_fields}
                totalReports
            }}
        }}
    }}
    """
    data, viewer = call_query(api_url, query, token=token)
    authors = data["authors"]

    for edge in authors["edges"]:
        edge["node"] = pythonize_author(edge["node"])

    return authors, viewer


def get_report_drafts(api_url, *, token=None):
    query = """
    reportDrafts {
        id
        date
        title
        body
    }
    """
    data, viewer = call_query(api_url, query, token=token)
    drafts = data["reportDrafts"]
    for draft in drafts:
        draft = pythonize_report(draft)
    return drafts, viewer
