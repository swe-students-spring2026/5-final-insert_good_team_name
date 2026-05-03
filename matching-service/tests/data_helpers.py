"""Helpers for tests to use"""


def make_user(age, algorithm_tags, loc=(0, 0), ranges=[(3, 10)], dietary=None):
    return {
        "age": age,
        "algorithm_tags": algorithm_tags,
        "location": loc,
        "preferred_group_ranges": ranges,
        "dietary_restrictions": dietary or [],
    }


def make_event(
    algorithm_tags, members, loc=(0, 0), capacity=6, *, dining=False, dining_tags=None
):
    return {
        "algorithm_tags": algorithm_tags,
        "location": loc,
        "attendees": members,
        "capacity": capacity,
        "dining_tags": dining_tags or [],
        "dining": dining,
    }
