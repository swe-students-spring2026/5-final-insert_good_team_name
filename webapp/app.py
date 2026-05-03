"""DinnerMeet Flask application."""

import os
import logging


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
from models.user import create_user
from models.event_model import create_event
from utils.validation import validate_signup, validate_login, validate_event
from utils.message import create_message, save_message, get_messages
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
    """Render app landing page for anonymous users."""
    if current_user.is_authenticated:
        return render_template("home.html")
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

    data = request.form

    error = validate_signup(data, users_collection)
    if error:
        return render_template("signup.html", error=error)

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
    emit("receive_message", msg, to=room)


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
        return render_template("create_event.html", error=error)

    event = create_event(data, current_user.id)

    result = events_collection.insert_one(event)

    users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$push": {"created_events": result.inserted_id}},
    )

    flash("Event created successfully.", "success")
    return redirect(url_for("events_page"))


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

        # find the oppose user
        user1, user2 = room.split("_", 1)
        other = user1 if user2 == user_id else user2

        # just keep the newest message
        if (
            room not in conversations
            or msg["timestamp"] > conversations[room]["timestamp"]
        ):
            conversations[room] = {
                "_id": room,
                "other_user": other,
                "last_message": msg["message"],
                "timestamp": msg["timestamp"],
            }

    return render_template(
        "messages.html",
        conversations=sorted(
            conversations.values(), key=lambda x: x["timestamp"], reverse=True
        ),
    )


@app.route("/chat/<username>", methods=["GET", "POST"])
@login_required
def chat(username):
    """Chat page: send + load messages"""
    room_id = "_".join(sorted([current_user.id, username]))

    # post = send message
    if request.method == "POST":
        text = request.form.get("message")

        if text:
            msg = create_message(room_id, current_user.id, text)
            save_message(messages_collection, msg)

        return redirect(url_for("chat", username=username))

    # get = load messages
    chat_messages = get_messages(messages_collection, room_id)

    return render_template("chat.html", messages=chat_messages, otherUsername=username)


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
                "host_id": {"$ne": current_user.id},
                "_id": {"$nin": rejected_events + joined_events + pending_events},
            }
        )
    )

    # Placeholder until matching-service scoring is integrated.
    best_event = get_best_event_match(user, candidate_events)

    return render_template("home.html", event=best_event)


@app.route("/events/<event_id>")
@login_required
def view_event(event_id):

    event = events_collection.find_one({"_id": ObjectId(event_id)})

    if not event:
        return "Event not found", 404

    host = users_collection.find_one({"_id": event["host_id"]})

    return render_template("event.html", event=event, host=host)


@app.route("/events/<event_id>/reject", methods=["POST"])
@login_required
def reject_event(event_id):
    users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$addToSet": {"rejected_events": ObjectId(event_id)}},
    )

    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    """Show user profile."""
    return render_template("profile.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
