from models.event_model import update_event
from models.user import update_user


def test_update_event_success():
    existing_event = {"image_url": "old-image.jpg"}

    data = {
        "description": "Updated event description",
        "location": "Brooklyn",
        "datetime": "2026-05-10T18:00",
        "capacity": "6",
        "dining": "on",
        "dining_tags": ["vegetarian", "halal"],
        "tags": ["restaurant_meetup", "coffee_meetup", "movie_night"],
        "image_url": "new-image.jpg",
    }

    event = update_event(data, existing_event)

    assert event["description"] == "Updated event description"
    assert event["location"] == "Brooklyn"
    assert event["datetime"] == "2026-05-10T18:00"
    assert event["capacity"] == 6
    assert event["dining"] is True
    assert event["dining_tags"] == ["vegetarian", "halal"]
    assert event["tags"] == ["restaurant_meetup", "coffee_meetup", "movie_night"]
    assert "algorithm_tags" in event
    assert event["image_url"] == "new-image.jpg"
    assert "updated_at" in event


def test_update_event_keeps_old_image_if_blank():
    existing_event = {"image_url": "old-image.jpg"}

    data = {
        "description": "Updated event description",
        "location": "Brooklyn",
        "datetime": "2026-05-10T18:00",
        "capacity": "6",
        "tags": ["restaurant_meetup", "coffee_meetup", "movie_night"],
        "image_url": "",
    }

    event = update_event(data, existing_event)

    assert event["image_url"] == "old-image.jpg"


def test_update_event_clears_dining_tags_when_not_dining():
    existing_event = {"image_url": "old-image.jpg"}

    data = {
        "description": "Updated event description",
        "location": "Brooklyn",
        "datetime": "2026-05-10T18:00",
        "capacity": "6",
        "tags": ["restaurant_meetup", "coffee_meetup", "movie_night"],
        "dining_tags": ["vegetarian"],
        "image_url": "",
    }

    event = update_event(data, existing_event)

    assert event["dining"] is False
    assert event["dining_tags"] == []


def test_update_user_success():
    data = {
        "neighborhood": "SoHo",
        "pronouns": "she/her",
        "dietary_restrictions": ["vegetarian"],
        "hobbies": ["theater"],
        "interests": ["music"],
        "drinks": "on",
    }

    user = update_user(data)

    assert user["neighborhood"] == "SoHo"
    assert user["pronouns"] == "she/her"
    assert user["dietary_restrictions"] == ["vegetarian"]
    assert user["hobbies"] == ["theater"]
    assert user["interests"] == ["music"]
    assert user["drinking_smoking"]["drinks"] is True
    assert user["drinking_smoking"]["smokes"] is False
    assert "updated_at" in user


def test_update_user_does_not_edit_name_age_email():
    data = {
        "neighborhood": "SoHo",
        "pronouns": "she/her",
        "dietary_restrictions": [],
        "hobbies": [],
        "interests": [],
    }

    user = update_user(data)

    assert "first_name" not in user
    assert "last_initial" not in user
    assert "age" not in user
    assert "email" not in user
    assert "password_hash" not in user
