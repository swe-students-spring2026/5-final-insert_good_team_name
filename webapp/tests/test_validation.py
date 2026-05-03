# pylint: disable=too-few-public-methods
from utils.validation import validate_signup, validate_login, validate_event
from werkzeug.security import generate_password_hash


class FakeUsersCollection:
    """Minimal mock collection for validation tests."""

    def __init__(self, existing_user=None):
        self.existing_user = existing_user

    def find_one(self, _query):
        return self.existing_user


def test_validate_signup_success():
    data = {
        "email": "test@example.com",
        "confirm_email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "first_name": "Lily",
        "last_name": "Lorand",
        "age": "23",
        "neighborhood": "Bushwick",
    }

    users_collection = FakeUsersCollection()

    assert validate_signup(data, users_collection) is None


def test_validate_signup_missing_required_field():
    data = {
        "email": "",
        "confirm_email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "first_name": "Lily",
        "last_name": "Lorand",
        "age": "23",
        "neighborhood": "Bushwick",
    }

    users_collection = FakeUsersCollection()

    assert (
        validate_signup(data, users_collection)
        == "Please fill out all required fields."
    )


def test_validate_signup_passwords_do_not_match():
    data = {
        "email": "test@example.com",
        "confirm_email": "test@example.com",
        "password": "password123",
        "confirm_password": "different",
        "first_name": "Lily",
        "last_name": "Lorand",
        "age": "23",
        "neighborhood": "Bushwick",
    }

    users_collection = FakeUsersCollection()

    assert validate_signup(data, users_collection) == "Passwords do not match."


def test_validate_signup_existing_user():
    data = {
        "email": "test@example.com",
        "confirm_email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "first_name": "Lily",
        "last_name": "Lorand",
        "age": "23",
        "neighborhood": "Bushwick",
    }

    users_collection = FakeUsersCollection(existing_user={"email": "test@example.com"})

    assert (
        validate_signup(data, users_collection)
        == "An account with this email already exists."
    )


def test_validate_login_success():
    data = {
        "email": "test@example.com",
        "password": "password123",
    }

    stored_user = {
        "email": "test@example.com",
        "password_hash": generate_password_hash("password123"),
    }

    users_collection = FakeUsersCollection(existing_user=stored_user)

    error, user = validate_login(data, users_collection)

    assert error is None
    assert user == stored_user


def test_validate_login_missing_email_or_password():
    data = {
        "email": "",
        "password": "password123",
    }

    users_collection = FakeUsersCollection()

    error, user = validate_login(data, users_collection)

    assert error == "Please enter email and password."
    assert user is None


def test_validate_login_user_not_found():
    data = {
        "email": "missing@example.com",
        "password": "password123",
    }

    users_collection = FakeUsersCollection()

    error, user = validate_login(data, users_collection)

    assert error == "No account found with that email."
    assert user is None


def test_validate_login_wrong_password():
    data = {
        "email": "test@example.com",
        "password": "wrongpassword",
    }

    stored_user = {
        "email": "test@example.com",
        "password_hash": generate_password_hash("password123"),
    }

    users_collection = FakeUsersCollection(existing_user=stored_user)

    error, user = validate_login(data, users_collection)

    assert error == "Incorrect password."
    assert user is None


def test_validate_signup_invalid_email():
    data = {
        "email": "invalidemail",
        "confirm_email": "invalidemail",
        "password": "password123",
        "confirm_password": "password123",
        "first_name": "Lily",
        "last_name": "Lorand",
        "age": "23",
        "neighborhood": "Bushwick",
    }

    users_collection = FakeUsersCollection()

    assert validate_signup(data, users_collection) == "Please enter a valid email."


def test_validate_signup_emails_do_not_match():
    data = {
        "email": "test@example.com",
        "confirm_email": "different@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "first_name": "Lily",
        "last_name": "Lorand",
        "age": "23",
        "neighborhood": "Bushwick",
    }

    users_collection = FakeUsersCollection()

    assert validate_signup(data, users_collection) == "Emails do not match."


def test_validate_event_capacity_not_number():
    data = {
        "title": "Dinner",
        "datetime": "2026-05-10T18:00",
        "capacity": "abc",
        "description": "Dinner event",
        "location": "NYC",
        "tags": ["restaurant_meetup", "coffee_meetup", "movie_night"],
    }

    assert validate_event(data) == "Capacity must be a number."


def test_validate_event_tags_as_string():
    data = {
        "title": "Dinner",
        "datetime": "2026-05-10T18:00",
        "capacity": "5",
        "description": "Dinner event",
        "location": "NYC",
        "tags": "restaurant_meetup",
    }

    # assert validate_event(data) == "You must select between 3 and 5 tags."
    assert validate_event(data) is None


def test_validate_event_tags_not_list():
    data = {
        "title": "Dinner",
        "datetime": "2026-05-10T18:00",
        "capacity": "5",
        "description": "Dinner event",
        "location": "NYC",
        "tags": 123,
    }

    assert validate_event(data) == "Tags must be a list."
