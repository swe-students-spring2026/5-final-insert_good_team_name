def create_message(room_id: str, sender: str, message: str) -> dict:
    """Create a message obj for db storage"""
    return {
        "room_id": room_id,
        "sender": sender,
        "message": message,
        "timestamp": datetime.utcnow()
    }

def save_message(collection, message_data: dict):
    """Save a message into the db"""
    return collection.insert_one(message_data)

def get_messages(collection, room_id: str):
    """Retrieve all messages from a specific chat room."""
    return list(collection.find({"room_id": room_id}))