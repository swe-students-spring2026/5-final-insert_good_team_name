# pylint: disable=redefined-outer-name, unnecessary-lambda

import pytest
from bson import ObjectId
import app
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


class FakeCursor:
    """mock mongodb cursor obj for testing"""

    def __init__(self, data):
        self.data = data

    def sort(self, key, order):
        reverse = order == -1
        self.data = sorted(self.data, key=lambda x: x.get(key, 0), reverse=reverse)
        return self

    def __iter__(self):
        return iter(self.data)


class FakeCollection:
    """mock db collection for testing"""

    def __init__(self, data=None):
        self.data = data or []

    def find(self, _):
        return FakeCursor(self.data)

    def find_one(self, query):
        for item in self.data:
            if "_id" in query and item["_id"] == query["_id"]:
                return item
        return None

    def insert_one(self, item):
        self.data.append(item)
        return True

    def update_one(self, _, __):
        return True


def test_chat_page(client, monkeypatch):
    user_id = str(ObjectId())
    other_id = str(ObjectId())

    fake_messages = [
        {
            "room_id": "_".join(sorted([user_id, other_id])),
            "sender": user_id,
            "message": "hi",
            "timestamp": 1,
        }
    ]

    monkeypatch.setattr(app, "messages_collection", FakeCollection(fake_messages))
    monkeypatch.setattr(app, "events_collection", FakeCollection([]))

    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: type("User", (), {"is_authenticated": True, "id": user_id})(),
    )

    response = client.get(f"/chat/{other_id}")

    assert response.status_code == 200


def test_apply_event(client, monkeypatch):
    user_id = str(ObjectId())
    host_id = str(ObjectId())
    event_id = ObjectId()

    fake_user = {
        "_id": ObjectId(user_id),
        "pending_events": [],
        "email": "test@test.com",
    }

    fake_event = {"_id": event_id, "host_id": ObjectId(host_id)}

    monkeypatch.setattr(app, "users_collection", FakeCollection([fake_user]))
    monkeypatch.setattr(app, "events_collection", FakeCollection([fake_event]))
    monkeypatch.setattr(app, "messages_collection", FakeCollection([]))

    with client.session_transaction() as sess:
        sess["_user_id"] = user_id

    response = client.post(f"/events/{event_id}/apply")

    assert response.status_code == 302


def test_accept_user(client, monkeypatch):
    event_id = ObjectId()
    user_id = str(ObjectId())
    host_id = str(ObjectId())

    monkeypatch.setattr(app, "events_collection", FakeCollection([]))
    monkeypatch.setattr(app, "users_collection", FakeCollection([]))
    monkeypatch.setattr(app, "messages_collection", FakeCollection([]))

    with client.session_transaction() as sess:
        sess["_user_id"] = host_id

    response = client.post(f"/events/{event_id}/accept/{user_id}")

    assert response.status_code == 302


def test_reject_user(client, monkeypatch):
    event_id = ObjectId()
    user_id = str(ObjectId())
    host_id = str(ObjectId())

    monkeypatch.setattr(app, "events_collection", FakeCollection([]))
    monkeypatch.setattr(app, "users_collection", FakeCollection([]))

    with client.session_transaction() as sess:
        sess["_user_id"] = host_id

    response = client.post(f"/events/{event_id}/reject_user/{user_id}")

    assert response.status_code == 302


def test_messages_page(client, monkeypatch):
    user_id = str(ObjectId())

    fake_messages = [
        {
            "room_id": "_".join(sorted([user_id, "2"])),
            "sender": user_id,
            "message": "hello",
            "timestamp": 1,
        }
    ]

    monkeypatch.setattr(app, "messages_collection", FakeCollection(fake_messages))
    monkeypatch.setattr(app, "users_collection", FakeCollection([]))

    monkeypatch.setattr(app, "render_template", lambda *args, **kwargs: "ok")

    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: type("User", (), {"is_authenticated": True, "id": user_id})(),
    )

    response = client.get("/messages")

    assert response.status_code == 200


def test_socket_connect(monkeypatch):
    user_id = str(ObjectId())

    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: type("User", (), {"is_authenticated": True, "id": user_id})(),
    )

    socket_client = app.socketIO.test_client(flask_app)

    assert socket_client.is_connected()


def test_join_room(monkeypatch):
    user_id = str(ObjectId())

    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: type("User", (), {"is_authenticated": True, "id": user_id})(),
    )

    socket_client = app.socketIO.test_client(flask_app)

    socket_client.emit("join_room", {"room": "test_room"})

    assert True


def test_send_message(monkeypatch):
    user_id = str(ObjectId())

    fake_collection = FakeCollection([])

    monkeypatch.setattr(app, "messages_collection", fake_collection)

    monkeypatch.setattr(
        app,
        "create_message",
        lambda room, sender, message: {
            "room_id": room,
            "sender": sender,
            "message": message,
            "timestamp": 0,
        },
    )

    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: type("User", (), {"is_authenticated": True, "id": user_id})(),
    )

    socket_client = app.socketIO.test_client(flask_app)

    socket_client.emit("send_message", {"room": "room1", "message": "hello"})

    assert len(fake_collection.data) == 1
