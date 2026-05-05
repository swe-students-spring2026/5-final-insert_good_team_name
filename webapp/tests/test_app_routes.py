# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock

import pytest
from bson import ObjectId

import app as app_module
from app import app


def fake_login(monkeypatch, user_id):
    fake_user = MagicMock()
    fake_user.id = str(user_id)
    fake_user.is_authenticated = True

    app.config["LOGIN_DISABLED"] = True
    monkeypatch.setattr(app_module, "current_user", fake_user)


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


def test_logout_requires_login(client):
    response = client.get("/logout")
    assert response.status_code == 302


def test_events_post_not_allowed(client):
    response = client.post("/events")
    assert response.status_code in [405, 302]


def test_create_event_post_not_allowed(client):
    response = client.post("/events/create")
    assert response.status_code in [405, 302]


def test_login_post_empty(client):
    response = client.post("/login", data={})
    assert response.status_code in [200, 302]


def test_signup_post_empty(client):
    response = client.post("/signup", data={})
    assert response.status_code in [200, 302]


def test_home_trailing_slash(client):
    response = client.get("/home/")
    assert response.status_code in [200, 302, 404]


def test_events_trailing_slash(client):
    response = client.get("/events/")
    assert response.status_code in [200, 302, 404]


def test_profile_trailing_slash(client):
    response = client.get("/profile/")
    assert response.status_code in [200, 302, 404]


def test_signup_existing_user(client, monkeypatch):
    from app import users_collection

    # mock DB: user already exists
    users_collection.find_one = MagicMock(return_value={"email": "test@test.com"})

    # bypass validation for testing flow
    monkeypatch.setattr("app.validate_signup", lambda data, _: None)

    monkeypatch.setattr(
        "app.render_template",
        lambda template, **kwargs: "signup error",
    )

    response = client.post(
        "/signup",
        data={
            "email": "test@test.com",
            "confirm_email": "test@test.com",
            "password": "pass",
            "confirm_password": "pass",
            "first_name": "A",
            "last_name": "B",
            "age": "20",
            "neighborhood": "NY",
        },
    )

    assert response.status_code == 200
    assert b"signup error" in response.data


def test_signup_success(client, monkeypatch):
    from app import users_collection

    # no existing user
    users_collection.find_one = MagicMock(return_value=None)

    # bypass validation
    monkeypatch.setattr("app.validate_signup", lambda data, _: None)

    # mock create_user
    monkeypatch.setattr(
        "app.create_user",
        lambda data: {"email": data["email"]},
    )

    # mock insert_one
    fake_result = MagicMock()
    fake_result.inserted_id = ObjectId()
    users_collection.insert_one = MagicMock(return_value=fake_result)

    response = client.post(
        "/signup",
        data={
            "email": "new@test.com",
            "confirm_email": "new@test.com",
            "password": "pass",
            "confirm_password": "pass",
            "first_name": "A",
            "last_name": "B",
            "age": "20",
            "neighborhood": "NY",
        },
    )

    assert response.status_code == 302
    assert "/" in response.location


def test_edit_event_not_found(client, monkeypatch):
    user_id = ObjectId()

    fake_login(monkeypatch, user_id)

    from app import events_collection

    events_collection.find_one = MagicMock(return_value=None)

    response = client.get(f"/events/{ObjectId()}/edit")

    assert response.status_code == 404
    assert b"Event not found" in response.data


def test_edit_event_unauthorized(client, monkeypatch):
    user_id = ObjectId()
    other_host_id = ObjectId()
    event_id = ObjectId()

    fake_login(monkeypatch, user_id)

    from app import events_collection

    events_collection.find_one = MagicMock(
        return_value={"_id": event_id, "host_id": other_host_id}
    )

    response = client.get(f"/events/{event_id}/edit")

    assert response.status_code == 403
    assert b"Unauthorized" in response.data


def test_edit_event_get_success(client, monkeypatch):
    user_id = ObjectId()
    event_id = ObjectId()

    fake_login(monkeypatch, user_id)

    from app import events_collection

    events_collection.find_one = MagicMock(
        return_value={"_id": event_id, "host_id": user_id}
    )

    monkeypatch.setattr(
        "app.render_template",
        lambda template, **kwargs: "edit event page",
    )

    response = client.get(f"/events/{event_id}/edit")

    assert response.status_code == 200
    assert b"edit event page" in response.data


def test_edit_event_post_success(client, monkeypatch):
    user_id = ObjectId()
    event_id = ObjectId()
    event = {"_id": event_id, "host_id": user_id, "title": "Old Title"}

    fake_login(monkeypatch, user_id)

    from app import events_collection

    events_collection.find_one = MagicMock(return_value=event)
    events_collection.update_one = MagicMock()

    monkeypatch.setattr("app.validate_event", lambda data: None)
    monkeypatch.setattr(
        "app.update_event", lambda data, old_event: {"location": "New York"}
    )

    response = client.post(
        f"/events/{event_id}/edit",
        data={
            "title": "Old Title",
            "date": "2026-05-10",
            "time": "18:00",
            "capacity": "5",
            "location": "New York",
            "description": "Dinner",
            "tags": ["casual"],
            "dining_tags": ["vegetarian"],
        },
    )

    assert response.status_code == 302
    assert f"/events/{event_id}" in response.location
    events_collection.update_one.assert_called_once()
