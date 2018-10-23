from .graphql import (
    NotFoundError,
    call_query,
    encode_global_id,
    decode_global_id,
    pythonize_report,
    pythonize_author,
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


def search_reports(api_url, slice, *, token=None):
    if "after" in slice:
        slice_info = """(query:"{query}", highlight:true, first:{first}, after:"{after}")""".format(
            **slice
        )
    else:
        slice_info = """(query:"{query}", highlight:true, first:{first})""".format(
            **slice
        )

    query = f"""
    searchReports {slice_info} {{
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


def get_author_with_reports(api_url, id, slice, *, token=None):
    if "after" in slice:
        slice_info = """(first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(first:{first})""".format(**slice)

    global_id = encode_global_id("Author", id)
    query = f"""
    node (id:"{global_id}") {{
        ... on Author {{
            {author_fields}
            reports {slice_info} {{
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


def get_authors(api_url, slice, *, token=None):
    if "after" in slice:
        slice_info = """(first:{first}, after:"{after}")""".format(**slice)
    else:
        slice_info = """(first:{first})""".format(**slice)

    query = f"""
    authors {slice_info} {{
        totalCount
        edges {{
            node {{
                {author_fields}
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
