"""DinnerMeet Flask application."""

import os
import random
import logging
from datetime import datetime
from typing import Dict

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from models.user import create_user
from models.event_model import create_event
from utils.validation import validate_signup, validate_login, validate_event
from db import users_collection, events_collection
from bson import ObjectId

# This is a placeholder function for the matching algorithm. It currently just returns the first event.
def get_best_event_match(user, events):
    if not events:
        return None

    return events[0]


load_dotenv()


#loggling
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ('true', "1", "t")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = os.environ.get("SECRET_KEY", "dev")
app.cors_origins


#Handle Reverse PRoxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)



class User(UserMixin):
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


@app.route("/events")
@login_required
def events():
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
        {"$push": {"created_events": result.inserted_id}}
    )

    flash("Event created successfully.", "success")
    return redirect(url_for("events"))

@app.route("/messages")
@login_required
def messages():
    """Show all message conversations."""
    return render_template("messages.html", conversations=[])

@app.route("/home")
@login_required
def home():
    user = users_collection.find_one({"_id": ObjectId(current_user.id)})

    rejected_events = user.get("rejected_events", [])
    joined_events = user.get("joined_events", [])
    pending_events = user.get("pending_events", [])

    events = list(events_collection.find({
        "event_open": True,
        "host_id": {"$ne": current_user.id},
        "_id": {
            "$nin": rejected_events + joined_events + pending_events
        }
    }))

    #TODO: create a function to calculate best match based on matching service algorithm
    best_event = get_best_event_match(user, events)

    return render_template("home.html", event=best_event)

from bson.objectid import ObjectId

@app.route("/events/<event_id>")
@login_required
def view_event(event_id):
    user_id = ObjectId(current_user.id)

    event = events_collection.find_one({"_id": ObjectId(event_id)})

    if not event:
        return "Event not found", 404

    # Restrict access (chat-only logic enforcement)
    if (
        user_id != event["host_id"]
        and user_id not in event.get("attendees", [])
        and user_id not in event.get("join_requests", [])
    ):
        return "Unauthorized", 403

    host = users_collection.find_one({"_id": event["host_id"]})

    return render_template(
        "event.html",
        event=event,
        host=host
    )

@app.route("/events/<event_id>/reject", methods=["POST"])
@login_required
def reject_event(event_id):
    users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$addToSet": {"rejected_events": ObjectId(event_id)}}
    )

    return redirect(url_for("home"))

@app.route("/profile")
@login_required
def profile():
    """Show user profile."""
    return render_template("profile.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
