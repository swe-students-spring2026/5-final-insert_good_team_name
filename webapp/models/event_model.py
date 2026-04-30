from datetime import datetime


def create_event(data, host_id, image_url=None):
    return {
        "title": data["title"],

        # REQUIRED fields 
        "description": data["description"],
        "location": data["location"],

        "date": data["date"],
        "time": data["time"],

        "host_id": host_id,
        "capacity": int(data["capacity"]),

        # Defaults
        "dining": bool(data.get("dining", False)),
        "dining_tags": data.get("dining_tags", []) if isinstance(data.get("dining_tags", []), list) else [],
        "tags": data.get("tags", []) if isinstance(data.get("tags", []), list) else [],

        "image_url": image_url,
        "event_open": True,

        # Host automatically joins
        "attendees": [host_id],
        # Pending and rejected lists to manage join requests
        "join_requests": [],
        "rejected_requests": [],

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }