"""
    Dummy conftest.py for pyeagleio.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest
import os
from typing import Dict
from pathlib import Path
import json
import pyeagleio.https


@pytest.fixture(scope="session")
def api_key() -> str:
    # Try get form ENV
    api_key = os.environ.get("EAGLEIO_APIKEY")
    if not api_key:
        pytest.skip("Could not get eagle API Key to use for tests, skipping")
    yield api_key


@pytest.fixture(scope="module")
def httpsclient(api_key) -> "pyeagleio.https.HTTPSClient":
    api = pyeagleio.https.HTTPSClient(api_key)
    yield api


@pytest.fixture(scope="session")
def example_jts() -> Dict:
    path = Path("tests") / "data" / "example-small.jts.json"
    jts = json.loads(path.read_text(encoding="utf-8"))
    yield jts
