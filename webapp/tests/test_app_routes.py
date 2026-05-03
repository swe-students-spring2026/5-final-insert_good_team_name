import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200


def test_login_get_route(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_signup_get_route(client):
    response = client.get("/signup")
    assert response.status_code == 200


def test_events_requires_login(client):
    response = client.get("/events")
    assert response.status_code == 302


def test_create_event_requires_login(client):
    response = client.get("/events/create")
    assert response.status_code == 302


def test_home_requires_login(client):
    response = client.get("/home")
    assert response.status_code == 302


def test_messages_requires_login(client):
    response = client.get("/messages")
    assert response.status_code == 302


def test_profile_requires_login(client):
    response = client.get("/profile")
    assert response.status_code == 302