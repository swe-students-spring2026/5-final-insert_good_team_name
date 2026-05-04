"""DinnerMeet Flask application."""

import os
import logging
import requests as http_requests


from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_socketio import SocketIO, emit, join_room
from werkzeug.middleware.proxy_fix import ProxyFix

from dotenv import load_dotenv
from models.user import create_user, update_user
from models.event_model import create_event, update_event
from utils.validation import validate_signup, validate_login, validate_event
from utils.message import create_message, save_message
from db import users_collection, events_collection, messages_collection


# Placeholder matching: return first eligible event.
def get_best_event_match(_user, candidate_events):
    if not candidate_events:
        return None

    return candidate_events[0]


load_dotenv()


# loggling
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class Config:
    """config for the socket"""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Handle Reverse PRoxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


# Set up the Socket
socketIO = SocketIO(
    app,
    cors_allowed_origins=app.config["CORS_ORIGINS"],
    logger=True,
    engineio_logger=True,
)


# pylint: disable=too-few-public-methods
class User(UserMixin):
    """Flask-Login wrapper for MongoDB user documents."""

    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]
        self.data = user_data


@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(user)
    return None


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Render login page."""
    if request.method == "GET":
        return render_template("login.html")

    data = request.form

    error, user_data = validate_login(data, users_collection)

    if error:
        return render_template("login.html", error=error)

    user = User(user_data)
    login_user(user)

    flash("Logged in successfully.", "success")
    return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Render signup page.
    Create a new user and log them in."""
    if request.method == "GET":
        return render_template("signup.html")

    data = request.form.to_dict()
    data["interests"] = request.form.getlist("interests")
    data["dietary_restrictions"] = request.form.getlist("dietary_restrictions")

    error = validate_signup(data, users_collection)
    if error:
        return render_template("signup.html", error=error, data=data)

    existing_user = users_collection.find_one({"email": data["email"]})
    if existing_user:
        return render_template("signup.html", error="User already exists.")

    user_data = create_user(data)
    result = users_collection.insert_one(user_data)

    user_data["_id"] = result.inserted_id
    user = User(user_data)
    login_user(user)

    flash("Account created successfully.", "success")
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    """Clear session and redirect to login."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# Make a connection
@socketIO.event
def connect():
    """handles conenction"""
    if not current_user.is_authenticated:
        return False

    logger.info("%s connected", current_user.id)
    return True


@socketIO.on("join_room")
def handle_join(data):
    """join a chat room."""
    room = data["room"]
    join_room(room)


@socketIO.on("send_message")
def handle_send_message(data):
    """Handle sending a message via socket"""
    if not current_user.is_authenticated:
        return

    room = data["room"]
    text = data["message"]

    msg = create_message(room, current_user.id, text)
    save_message(messages_collection, msg)

    emit(
        "receive_message",
        {
            "room_id": room,
            "sender": current_user.id,
            "message": text,
            "timestamp": msg["timestamp"].isoformat(),
        },
        to=room,
    )


@app.route("/events")
@login_required
def events_page():
    """Show all events."""
    return render_template("events.html", events=[])


@app.route("/events/create", methods=["GET", "POST"])
@login_required
def create_event_route():
    """Create a new event."""
    if request.method == "GET":
        return render_template("create_event.html")

    data = request.form.to_dict()
    data["tags"] = request.form.getlist("tags")

    error = validate_event(data)
    if error:
        return render_template("create_event.html", error=error, data=data)

    event = create_event(data, ObjectId(current_user.id))

    result = events_collection.insert_one(event)

    users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$push": {"created_events": result.inserted_id}},
    )

    flash("Event created successfully.", "success")
    return redirect(url_for("events_page"))


@app.route("/events/<event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    """Edit an event (host only)."""

    event = events_collection.find_one({"_id": ObjectId(event_id)})

    if not event:
        return "Event not found", 404

    # Only host can edit
    if str(event["host_id"]) != current_user.id:
        return "Unauthorized", 403

    if request.method == "GET":
        return render_template("edit_event.html", event=event)

    data = request.form.to_dict()

    # multi-select fields
    data["tags"] = request.form.getlist("tags")
    data["dining_tags"] = request.form.getlist("dining_tags")

    # Validate (same as create, since title is hidden in form)
    error = validate_event(data)
    if error:
        return render_template("edit_event.html", event=event, error=error)

    # Update event with new data while keeping unchanged fields intact
    updated_event = update_event(data, event)

    events_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": updated_event},
    )

    flash("Event updated successfully.", "success")
    return redirect(url_for("view_event", event_id=event_id))


@app.route("/messages")
@login_required
def messages():
    """Show all message conversations."""
    user_id = current_user.id

    all_messages = list(
        messages_collection.find(
            {
                "$or": [
                    {"sender": user_id},
                    {"room_id": {"$regex": f"^{user_id}_|_{user_id}$"}},
                ]
            }
        )
    )

    conversations = {}

    for msg in all_messages:
        room = msg["room_id"]
        user1, user2 = room.split("_", 1)
        other_id = user1 if user2 == user_id else user2

        # Look up other user's name
        other_user = users_collection.find_one({"_id": ObjectId(other_id)})
        if other_user:
            other_name = f"{other_user.get('first_name', '')} {other_user.get('last_initial', '')}."
        else:
            other_name = other_id

        if (
            room not in conversations
            or msg["timestamp"] > conversations[room]["timestamp"]
        ):
            conversations[room] = {
                "_id": room,
                "other_user": other_id,
                "other_name": other_name,
                "last_message": msg["message"],
                "timestamp": msg["timestamp"],
            }

    return render_template(
        "messages.html",
        conversations=sorted(
            conversations.values(), key=lambda x: x["timestamp"], reverse=True
        ),
    )


@app.route("/chat/<user_id>", methods=["GET"])
@login_required
def chat(user_id):
    """Chat page"""

    room_id = "_".join(sorted([current_user.id, user_id]))

    chat_messages = list(
        messages_collection.find({"room_id": room_id}).sort("timestamp", 1)
    )

    host_obj_id = ObjectId(user_id)
    current_obj_id = ObjectId(current_user.id)

    other_user = users_collection.find_one({"_id": host_obj_id})
    if other_user:
        other_name = (
            f"{other_user.get('first_name', '')} "
            f"{other_user.get('last_initial', '')}."
        )
    else:
        other_name = user_id

    shared_events = list(
        events_collection.find(
            {
                "$and": [
                    {
                        "$or": [
                            {"host_id": host_obj_id},
                            {"attendees": host_obj_id},
                            {"join_requests": host_obj_id},
                        ]
                    },
                    {
                        "$or": [
                            {"host_id": current_obj_id},
                            {"attendees": current_obj_id},
                            {"join_requests": current_obj_id},
                        ]
                    },
                ]
            }
        )
    )

    return render_template(
        "chat.html",
        messages=chat_messages,
        otherUsername=user_id,
        other_name=other_name,
        shared_events=shared_events,
    )


@app.route("/home")
@login_required
def home():
    user = users_collection.find_one({"_id": ObjectId(current_user.id)})

    rejected_events = user.get("rejected_events", [])
    joined_events = user.get("joined_events", [])
    pending_events = user.get("pending_events", [])

    candidate_events = list(
        events_collection.find(
            {
                "event_open": True,
                "host_id": {"$ne": ObjectId(current_user.id)},
                "_id": {"$nin": rejected_events + joined_events + pending_events},
            }
        )
    )

    user_payload = {
        "age": user.get("age"),
        "algorithm_tags": user.get("algorithm_tags", []),
        "neighborhood": user.get("neighborhood", ""),
        "preferred_group_ranges": user.get("preferred_group_ranges", [(3, 10)]),
        "dietary_restrictions": user.get("dietary_restrictions", []),
        "drinking_smoking": user.get("drinking_smoking", {}),
    }

    events_payload = []
    for e in candidate_events:
        event_dict = dict(e)
        event_dict["_id"] = str(event_dict["_id"])
        if "host_id" in event_dict:
            event_dict["host_id"] = str(event_dict["host_id"])
        event_dict["attendees"] = [str(a) for a in event_dict.get("attendees", [])]
        events_payload.append(event_dict)

    best_event = None
    try:
        matching_url = os.environ.get(
            "MATCHING_SERVICE_URL", "http://matching-service:5001"
        )
        response = http_requests.post(
            f"{matching_url}/match",
            json={"user": user_payload, "events": events_payload},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            best_event = data.get("best_event")
    except (ConnectionError, TimeoutError):
        # Fallback to first event if matching service unavailable
        best_event = events_payload[0] if events_payload else None

    return render_template("home.html", event=best_event)


# For users
@app.route("/events/<event_id>")
@login_required
def view_event(event_id):
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        return "Event not found", 404

    host = users_collection.find_one({"_id": event["host_id"]})

    requesters = []
    for req_id in event.get("join_requests", []):
        user = users_collection.find_one({"_id": req_id})
        if user:
            requesters.append(user)

    attendees = []
    for att_id in event.get("attendees", []):
        if str(att_id) != current_user.id:
            user = users_collection.find_one({"_id": att_id})
            if user:
                attendees.append(user)

    return render_template(
        "event.html",
        event=event,
        host=host,
        requesters=requesters,
        attendees=attendees,
        is_host=str(event["host_id"]) == current_user.id,
    )


@app.route("/events/<event_id>/apply", methods=["POST"])
@login_required
def apply_event(event_id):
    """User applies to the event."""
    user_id = current_user.id
    event_obj_id = ObjectId(event_id)

    # look up event
    event = events_collection.find_one({"_id": event_obj_id})
    if not event:
        return "Event not found", 404

    host_id = str(event["host_id"])

    user = users_collection.find_one({"_id": ObjectId(user_id)})

    # prevent repeated applications
    if event_obj_id in user.get("pending_events", []):
        return redirect(url_for("chat", user_id=host_id))

    # update user to pending
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"pending_events": event_obj_id}},
    )

    # update join requests
    events_collection.update_one(
        {"_id": event_obj_id},
        {"$addToSet": {"join_requests": ObjectId(user_id)}},
    )

    # create new chat room
    room_id = "_".join(sorted([user_id, host_id]))

    # send automated message
    msg_text = (
        f"Hi! I would like to join your event:" f" '{event.get('title', 'Untitled')}'."
    )
    msg = create_message(room_id, user_id, msg_text)

    save_message(messages_collection, msg)

    return redirect(url_for("chat", user_id=host_id))


@app.route("/events/<event_id>/reject", methods=["POST"])
@login_required
def reject_event(event_id):
    users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$addToSet": {"rejected_events": ObjectId(event_id)}},
    )

    return redirect(url_for("home"))


# These are for hosts
@app.route("/events/<event_id>/accept/<user_id>", methods=["POST"])
@login_required
def accept_user(event_id, user_id):
    """host accepts a user into event"""
    event_obj_id = ObjectId(event_id)
    user_obj_id = ObjectId(user_id)

    # update from pending to attendees.
    events_collection.update_one(
        {"_id": event_obj_id},
        {
            "$pull": {"join_requests": user_obj_id},
            "$addToSet": {"attendees": user_obj_id},
        },
    )

    # update user
    users_collection.update_one(
        {"_id": user_obj_id},
        {
            "$pull": {"pending_events": event_obj_id},
            "$addToSet": {"joined_events": event_obj_id},
        },
    )

    # send approval message
    room_id = "_".join(sorted([str(user_id), current_user.id]))

    msg = create_message(
        room_id, current_user.id, "You have been accepted to the event!"
    )

    save_message(messages_collection, msg)

    return redirect(url_for("view_event", event_id=event_id))


@app.route("/events/<event_id>/reject_user/<user_id>", methods=["POST"])
@login_required
def reject_user(event_id, user_id):
    """Host rejects a user"""
    event_obj_id = ObjectId(event_id)
    user_obj_id = ObjectId(user_id)

    # remove from join requests
    events_collection.update_one(
        {"_id": event_obj_id},
        {"$pull": {"join_requests": user_obj_id}},
    )

    # update users
    users_collection.update_one(
        {"_id": user_obj_id},
        {
            "$pull": {"pending_events": event_obj_id},
            "$addToSet": {"rejected_events": event_obj_id},
        },
    )

    return redirect(url_for("view_event", event_id=event_id))


@app.route("/profile")
@login_required
def profile():
    """Show user profile."""
    return render_template("profile.html")


@app.route("/my-events")
@login_required
def my_events():
    """Show events the user is hosting and attending."""
    user = users_collection.find_one({"_id": ObjectId(current_user.id)})

    hosted = list(events_collection.find({"host_id": ObjectId(current_user.id)}))

    joined_ids = user.get("joined_events", [])
    attending = list(events_collection.find({"_id": {"$in": joined_ids}}))

    pending_ids = user.get("pending_events", [])
    pending = list(events_collection.find({"_id": {"$in": pending_ids}}))

    return render_template(
        "my_events.html", hosted=hosted, attending=attending, pending=pending
    )


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edit current user's profile (restricted fields only)."""

    user = users_collection.find_one({"_id": ObjectId(current_user.id)})

    if not user:
        return "User not found", 404

    if request.method == "GET":
        return render_template("edit_profile.html", user=user)

    data = request.form.to_dict()

    data["dietary_restrictions"] = request.form.getlist("dietary_restrictions")
    data["interests"] = request.form.getlist("interests")
    data["hobbies"] = request.form.get("hobbies", "")

    updated_user = update_user(data)

    users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": updated_user},
    )

    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/events/<event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    """Host deletes an event."""
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event or str(event["host_id"]) != current_user.id:
        return redirect(url_for("my_events"))

    events_collection.delete_one({"_id": ObjectId(event_id)})

    users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$pull": {"created_events": ObjectId(event_id)}},
    )

    flash("Event deleted.", "success")
    return redirect(url_for("my_events"))


@app.route("/users/<user_id>")
@login_required
def view_user(user_id):
    """View another user's profile."""
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return "User not found", 404
    return render_template("view_user.html", user=user)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
