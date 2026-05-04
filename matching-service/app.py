"""Simple matching service API."""

import os
from flask import Flask, jsonify, request
from bson import ObjectId

from matching.event_match import compute_match_score
from db import users_collection

app = Flask(__name__)


def mongo_user_lookup(user_id):
    """
    Fetch full user document from MongoDB
    """
    if not user_id:
        return None

    try:
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
    except Exception:
        return None

    doc = users_collection.find_one({"_id": user_id})
    if not doc:
        return None

    return {
        "age": doc.get("age"),
        "algorithm_tags": doc.get("algorithm_tags", []),
        "neighborhood": doc.get("neighborhood"),
        "preferred_group_ranges": doc.get("preferred_group_ranges", [(3, 10)]),
        "dietary_restrictions": doc.get("dietary_restrictions", []),
        "drinks": doc.get("drinking_smoking", {}).get("drinks", True),
        "smokes": doc.get("drinking_smoking", {}).get("smokes", False),
    }


@app.post("/match")
def match():
    payload = request.get_json(silent=True) or {}

    user = payload.get("user")
    events = payload.get("events", [])

    if not user or not events:
        return jsonify({"best_event": None, "score": 0.0}), 400

    best_event = None
    best_score = float("-inf")

    for event in events:
        event_id = event.get("_id")
        if isinstance(event_id, str):
            event["_id"] = ObjectId(event_id)

        score = compute_match_score(user, event, mongo_user_lookup)

        if score > best_score:
            best_score = score
            best_event = event

    return jsonify(
        {"best_event": serialize_event(best_event), "score": max(best_score, 0.0)}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5001")), debug=True)


def serialize_event(event):
    if not event:
        return None

    event = dict(event)

    if "_id" in event:
        event["_id"] = str(event["_id"])

    return event
