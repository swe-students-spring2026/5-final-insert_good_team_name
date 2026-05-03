from datetime import datetime
from utils.tag_transformer import transform_event_type_to_tags


def create_event(data, host_id, image_url=None):
    selected_tags = data.get("tags", [])
    return {
        "title": data["title"],
        # REQUIRED fields
        "description": data["description"],
        "location": data["location"],
        "datetime": data["datetime"],
        "host_id": host_id,
        "capacity": int(data["capacity"]),
        # Defaults
        "dining": bool(data.get("dining", False)),
        "dining_tags": (
            data.get("dining_tags", [])
            if isinstance(data.get("dining_tags", []), list)
            else []
        ),
        "tags": selected_tags if isinstance(selected_tags, list) else [],
        "algorithm_tags": transform_event_type_to_tags(selected_tags),
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
