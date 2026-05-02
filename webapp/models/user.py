from datetime import datetime
from werkzeug.security import generate_password_hash


def create_user(data):
    return {
        "email": data["email"],
        "password_hash": generate_password_hash(data["password"]),
        "first_name": data["first_name"],
        "last_initial": data["last_name"][0] if data.get("last_name") else "",
<<<<<<< HEAD
=======

>>>>>>> 33a306e9386eec4cd8d06199c80cd9ce6691b1fd
        "age": int(data["age"]),
        "neighborhood": data["neighborhood"],
        "pronouns": data.get("pronouns"),
        "drinking_smoking": {
            "drinks": data.get("drinks"),
            "smokes": data.get("smokes"),
        },
<<<<<<< HEAD
        "dietary_restrictions": data.get("dietary_restrictions", []),
=======

        "dietary_restrictions": data.get("dietary_restrictions", []), #Change to preferences?
>>>>>>> 33a306e9386eec4cd8d06199c80cd9ce6691b1fd
        "hobbies": data.get("hobbies", []),
        "interests": data.get("interests", []),
        "created_events": [],
        "joined_events": [],
        "rejected_events": [],
        "pending_events": [],
<<<<<<< HEAD
=======

>>>>>>> 33a306e9386eec4cd8d06199c80cd9ce6691b1fd
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
