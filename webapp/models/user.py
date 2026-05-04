from datetime import datetime
from werkzeug.security import generate_password_hash
from utils.tag_transformer import transform_preferences_to_tags


def create_user(data):
    interests = data.get("interests", [])
    return {
        "email": data["email"],
        "password_hash": generate_password_hash(data["password"]),
        "first_name": data["first_name"],
        "last_initial": data["last_name"][0] if data.get("last_name") else "",
        "age": int(data["age"]),
        "neighborhood": data["neighborhood"],
        "pronouns": data.get("pronouns"),
        "drinking_smoking": {
            "drinks": data.get("drinks") == "yes",
            "smokes": data.get("smokes") == "yes",
        },
        "dietary_restrictions": data.get("dietary_restrictions", []),
        "hobbies": data.get("hobbies", ""),
        "interests": data.get("interests", []),
        "algorithm_tags": transform_preferences_to_tags(data.get("interests", [])),
        "created_events": [],
        "joined_events": [],
        "rejected_events": [],
        "pending_events": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def update_user(data):
    return {
        "neighborhood": data["neighborhood"],
        "pronouns": data.get("pronouns", ""),
        "dietary_restrictions": data.get("dietary_restrictions", []),
        "hobbies": data.get("hobbies", ""),
        "interests": data.get("interests", []),
        "algorithm_tags": transform_preferences_to_tags(data.get("interests", [])),
        "drinking_smoking": {
            "drinks": data.get("drinks") == "yes",
            "smokes": data.get("smokes") == "yes",
        },
        "updated_at": datetime.utcnow(),
    }
