def make_user(age, tags, loc=(0, 0), ranges=[(3, 10)], dietary=None):
    return {
        "age": age,
        "tags": tags,
        "location": loc,
        "preferred_group_ranges": ranges,
        "dietary_restrictions": dietary or [],
    }


def make_event(
    tags, members, loc=(0, 0), intended_size=6, dining_tags=None, dining=False
):
    return {
        "tags": tags,
        "location": loc,
        "attendees": members,
        "capacity": intended_size,
        "dining_tags": dining_tags or [],
        "dining": dining,
    }
