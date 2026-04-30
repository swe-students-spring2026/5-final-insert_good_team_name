from datetime import datetime
from utils.message import create_message, save_message, get_messages

class FakeCollection:
    def __init__(self):
        self.data = []

    def insert_one(self, item):
        self.data.append(item)
        return True
    
    def find(self, query):
        return [m for m in self.data if m["room_id"] == query["room_id"]]
    

def test_create_message():
    msg = create_message("room1", "user1", "hello")
    
    assert msg["room_id"] == "room1"
    assert msg["sender"] == "user1"
    assert msg["message"] == "hello"
    assert "timestamp" in msg


def test_save_message():
    collection = FakeCollection()

    msg = create_message("room1", "user1", "hi")
    result = save_message(collection, msg)

    assert len(collection.data) == 1
    assert collection.data[0]["message"] == "hi"


def test_get_messages():
    collection = FakeCollection()

    msg1 = create_message("room1", "user1", "hi")
    msg2 = create_message("room1", "user2", "yo")
    msg3 = create_message("room2", "user3", "other room")

    collection.insert_one(msg1)
    collection.insert_one(msg2)
    collection.insert_one(msg3)

    result = get_messages(collection, "room1")

    assert len(result) == 2