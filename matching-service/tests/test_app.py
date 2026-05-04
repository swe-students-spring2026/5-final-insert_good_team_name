import json
from bson import ObjectId

from app import app


class FakeUsersCollection:
    def __init__(self, users):
        self.users = users

    def find_one(self, query):
        uid = query.get("_id")

        # Mongo expects ObjectId — enforce it
        if not isinstance(uid, ObjectId):
            return None

        return self.users.get(uid)


def setup_fake_db(monkeypatch):
    user_id = ObjectId()

    fake_users = {
        user_id: {
            "_id": user_id,
            "age": 25,
            "interests": ["outdoors"],
            "neighborhood": "Chelsea",
            "preferred_group_ranges": [(3, 10)],
            "dietary_restrictions": [],
            "drinking_smoking": {"drinks": True, "smokes": False},
        }
    }

    fake_collection = FakeUsersCollection(fake_users)

    monkeypatch.setattr("app.users_collection", fake_collection)

    return str(user_id)


def test_match_basic(monkeypatch):
    user_id = setup_fake_db(monkeypatch)

    client = app.test_client()

    payload = {
        "user": {
            "age": 25,
            "algorithm_tags": ["outdoors"],
            "neighborhood": "Chelsea",
            "preferred_group_ranges": [(3, 10)],
            "dietary_restrictions": [],
        },
        "events": [
            {
                "_id": user_id,
                "algorithm_tags": ["outdoors"],
                "location": "Chelsea",
                "attendees": [user_id],
                "capacity": 6,
                "dining": False,
                "dining_tags": [],
            }
        ],
    }

    res = client.post("/match", json=payload)

    assert res.status_code == 200

    data = res.get_json()

    assert "best_event" in data
    assert "score" in data
    assert data["score"] >= 0.0


def test_match_prefers_better_event(monkeypatch):
    user_id = setup_fake_db(monkeypatch)

    client = app.test_client()

    payload = {
        "user": {
            "age": 25,
            "algorithm_tags": ["outdoors"],
            "neighborhood": "Chelsea",
            "preferred_group_ranges": [(3, 10)],
            "dietary_restrictions": [],
        },
        "events": [
            {
                "_id": str(ObjectId()),
                "algorithm_tags": ["gaming"],  # worse match
                "location": "Inwood",
                "attendees": [user_id],
                "capacity": 6,
                "dining": False,
                "dining_tags": [],
            },
            {
                "_id": str(ObjectId()),
                "algorithm_tags": ["outdoors"],  # better match
                "location": "Chelsea",
                "attendees": [user_id],
                "capacity": 6,
                "dining": False,
                "dining_tags": [],
            },
        ],
    }

    res = client.post("/match", json=payload)

    res = client.post("/match", json=payload)
    data = res.get_json()

    best_event = data["best_event"]

    assert best_event["algorithm_tags"] == ["outdoors"]


def test_match_empty_events(monkeypatch):
    setup_fake_db(monkeypatch)

    client = app.test_client()

    payload = {
        "user": {
            "age": 25,
            "algorithm_tags": ["outdoors"],
            "neighborhood": "Chelsea",
        },
        "events": [],
    }

    res = client.post("/match", json=payload)

    assert res.status_code == 400

    data = res.get_json()
    assert data["best_event"] is None
    assert data["score"] == 0.0


def test_match_missing_user(monkeypatch):
    setup_fake_db(monkeypatch)

    client = app.test_client()

    payload = {"events": []}

    res = client.post("/match", json=payload)

    assert res.status_code == 400


def test_objectid_conversion(monkeypatch):
    user_id = setup_fake_db(monkeypatch)

    client = app.test_client()

    payload = {
        "user": {
            "age": 25,
            "algorithm_tags": ["outdoors"],
            "neighborhood": "Chelsea",
        },
        "events": [
            {
                "_id": user_id,  # string → should convert
                "algorithm_tags": ["outdoors"],
                "location": "Chelsea",
                "attendees": [user_id],
                "capacity": 6,
                "dining": False,
                "dining_tags": [],
            }
        ],
    }

    res = client.post("/match", json=payload)

    assert res.status_code == 200


def test_match_api_contract(client):
    payload = {
        "user": {
            "age": 25,
            "algorithm_tags": ["outdoors"],
            "neighborhood": "Chelsea",
            "preferred_group_ranges": [(3, 10)],
            "dietary_restrictions": [],
            "drinks": True,
        },
        "events": [
            {
                "_id": "507f1f77bcf86cd799439011",
                "algorithm_tags": ["outdoors"],
                "location": "Chelsea",
                "attendees": [],
                "capacity": 5,
                "dining": False,
                "dining_tags": [],
            }
        ],
    }

    res = client.post("/match", json=payload)

    assert res.status_code == 200
    data = res.get_json()

    assert "best_event" in data
    assert "score" in data
    assert isinstance(data["score"], float)
