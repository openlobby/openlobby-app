from ..graphql import (
    decode_global_id,
    encode_global_id,
    encode_cursor,
    encode_arguments,
    str_argument,
)


def test_decode_global_id():
    # encoded value: User:ABC123
    assert decode_global_id("VXNlcjpBQkMxMjM=") == ["User", "ABC123"]


def test_encode_global_id():
    assert encode_global_id("User", "ABC123") == "VXNlcjpBQkMxMjM="


def test_encode_cursor():
    assert encode_cursor(42) == "NDI="


def test_str_argument():
    assert str_argument("foo") == '"foo"'


def test_encode_arguments():
    arguments = {
        "first": 7,
        "after": str_argument("ABC"),
        "query": str_argument("foo"),
        "sort": "NAME",
        "reversed": "true",
    }
    expected = 'first: 7, after: "ABC", query: "foo", sort: NAME, reversed: true'
    assert encode_arguments(arguments) == expected
