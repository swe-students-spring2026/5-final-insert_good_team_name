from matching.event_match import compute_match_score


def get_best_event(user, event_docs, users_collection):
    """
    Returns the best event from event_docs for the user,
    ignores events the user already interacted with

    user = {
        "age": int,
        "algorithm_tags": List[str],
        "location": (lat, lon),
        "preferred_group_ranges": List[(min, max)],
        "dietary_restrictions": List[str],
    }

    event = {
        "algorithm_tags": List[str],
        "location": (lat, lon),
        "attendees": List[str],
        "capacity": int,
        "dining": bool,
        "dining_tags": List[str],
    }

    users_collection: database collection used to fetch user documents by _id
    """
    if not event_docs:
        return None, 0.0

    # Categories of already interacted with events
    excluded_ids = set(
        user.get("created_events", [])
        + user.get("joined_events", [])
        + user.get("rejected_events", [])
        + user.get("pending_events", [])
    )

    event_docs = [e for e in event_docs if e.get("_id") not in excluded_ids]

    if not event_docs:
        return None, 0.0

    all_ids = set()
    for event in event_docs:
        all_ids.update(event.get("attendees", []))

    user_lookup = build_user_lookup(all_ids, users_collection)

    best_event = None
    best_score = -1

    for event in event_docs:
        score = compute_match_score(user, event, user_lookup)

        if score > best_score:
            best_score = score
            best_event = event

    return best_event, best_score


def get_ranked_events(user, event_docs, users_collection):
    """
    Returns an ordered list of events from event_docs for the user

    user = {
        "age": int,
        "algorithm_tags": List[str],
        "location": (lat, lon),
        "preferred_group_ranges": List[(min, max)],
        "dietary_restrictions": List[str],
    }

    event = {
        "algorithm_tags": List[str],
        "location": (lat, lon),
        "attendees": List[str],
        "capacity": int,
        "dining": bool,
        "dining_tags": List[str],
    }

    users_collection: database collection used to fetch user documents by _id
    """
    all_ids = set()
    for e in event_docs:
        all_ids.update(e.get("attendees", []))

    user_lookup = build_user_lookup(all_ids, users_collection)

    scored = []

    for event in event_docs:
        score = compute_match_score(user, event, user_lookup)
        scored.append((event, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return scored


def build_user_lookup(user_ids, users_collection):
    """
    Helper to make a user lookup
    """
    if not user_ids:
        return lambda uid: None

    docs = users_collection.find({"_id": {"$in": list(user_ids)}})

    cache = {str(doc["_id"]): doc for doc in docs}

    return lambda uid: cache.get(str(uid))
