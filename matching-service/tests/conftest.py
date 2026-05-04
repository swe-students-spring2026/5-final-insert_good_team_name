"""Pytest setup: ensure matching-service root is importable (e.g. `import app`)."""

import sys
from pathlib import Path

import pytest
from app import app

_SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(_SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SERVICE_ROOT))


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
