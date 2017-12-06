from ..graphql import (
    decode_global_id,
    encode_global_id,
    encode_cursor,
)


def test_decode_global_id():
    # encoded value: User:ABC123
    assert decode_global_id('VXNlcjpBQkMxMjM=') == ['User', 'ABC123']


def test_encode_global_id():
    assert encode_global_id('User', 'ABC123') == 'VXNlcjpBQkMxMjM='


def test_encode_cursor():
    assert encode_cursor(42) == 'NDI='
