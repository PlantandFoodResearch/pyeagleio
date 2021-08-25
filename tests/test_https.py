import pytest
from pyeagleio.https import HTTPSClient


def test_basic(api_key):
    _ = HTTPSClient(api_key)


def test_bad_api_key():
    with pytest.raises(ValueError) as exc:
        _ = HTTPSClient("bad_key")
    assert "Unauthorized" in str(exc)
