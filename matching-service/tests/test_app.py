"""Tests for the matching-service Flask app."""

# pylint: disable=redefined-outer-name

import pytest

from app import app as flask_app


@pytest.fixture
def flask_test_client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


def test_match_post_returns_payload(flask_test_client):
    payload = {"user_id": 1}
    response = flask_test_client.post("/match", json=payload)
    assert response.status_code == 200
    assert response.get_json() == {"matched": True, "input": payload}
