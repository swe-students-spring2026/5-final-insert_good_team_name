import math
from typing import List, Tuple


def compute_match_score(user, event, user_lookup) -> float:
    """
    Calculates match score between a user and an event.

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

    user_lookup = map for uid to struct
    """

    # Event Score

    interest_event = list_similarity(user["algorithm_tags"], event["algorithm_tags"])
    dist_score = distance_score(user["location"], event["location"])

    event_score = 0.7 * interest_event + 0.3 * dist_score

    # Group Score

    member_ids = event.get("attendees", [])

    members = [user_lookup(uid) for uid in member_ids if user_lookup(uid) is not None]

    interest_group = sum(
        list_similarity(user["algorithm_tags"], m["algorithm_tags"]) for m in members
    ) / len(members)

    group_ages = [m["age"] for m in members]
    age_comp = age_score(user["age"], group_ages)

    group_score = 0.7 * interest_group + 0.3 * age_comp

    # Size Score

    size_score = calculate_size_score(
        event.get("capacity", 6), user.get("preferred_group_ranges", [(3, 10)])
    )

    # Dietary multiplier

    if event.get("dining", False):
        dietary_multiplier = dietary_score(
            user.get("dietary_restrictions", []), event.get("dining_tags", [])
        )
    else:
        dietary_multiplier = 1.0

    # Drinks multiplier

    if "drinks" in event["algorithm_tags"]:
        drinks_multiplier = get_drinks_multiplier(user)
    else:
        drinks_multiplier = 1.0

    return (
        (0.3 * event_score + 0.5 * group_score + 0.2 * size_score)
        * dietary_multiplier
        * drinks_multiplier
    )


def list_similarity(a: List[str], b: List[str]) -> float:
    """
    Returns a value based on how similar preference
    tags are to event tags in [0.0, 1.0]
    """
    set_a, set_b = set(a), set(b)
    if not set_a and not set_b:
        return 1.0

    intersection = len(set_a & set_b)

    covered = intersection / len(set_a) if set_a else 1.0

    union = len(set_a | set_b)
    overlap = intersection / union if union else 0.0

    return 0.7 * covered + 0.3 * overlap


def haversine_distance_km(
    loc1: Tuple[float, float], loc2: Tuple[float, float]
) -> float:
    """
    Helper for distance math
    """
    lat1, lon1 = loc1
    lat2, lon2 = loc2

    R = 6371  # Radius of earth

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def distance_score(user_loc, event_loc) -> float:
    """
    Returns a value based on distance from event in [0.0, 1.0]
    """
    d = haversine_distance_km(user_loc, event_loc)
    d = min(d, 50)
    return math.exp(-d / 10)


def distance_to_range(n: int, r_min: int, r_max: int) -> int:
    """
    Helper for math
    """
    if r_min <= n <= r_max:
        return 0
    return min(abs(n - r_min), abs(n - r_max))


def calculate_size_score(n: int, ranges: List[Tuple[int, int]]) -> float:
    """
    Returns a value based on size preference compared
    to capacity in [0.0, 1.0]
    """
    if not ranges:
        return 0.5

    best_distance = min(distance_to_range(n, r[0], r[1]) for r in ranges)
    return math.exp(-best_distance / 3)


def age_score(user_age: int, group_ages: List[int]) -> float:
    """
    Returns a value based on age similarity in [0.0, 1.0]
    """
    mean = sum(group_ages) / len(group_ages)
    variance = sum((a - mean) ** 2 for a in group_ages) / len(group_ages)
    std = math.sqrt(variance)

    return math.exp(-((user_age - mean) ** 2) / (2 * (std**2 + 4)))


def dietary_score(user_restrictions, event_dining_tags) -> float:
    """
    Returns a multiplier in [penalty_min, 1.0]
    """

    if not user_restrictions:
        return 1.0

    set_u = set(user_restrictions)
    set_e = set(event_dining_tags or [])

    matches = len(set_u & set_e)

    coverage = matches / len(set_u)

    penalty_min = 0.5

    return penalty_min + (1 - penalty_min) * coverage


def get_drinks_multiplier(user) -> float:
    """
    Returns a multiplier based on if user legally
    can and chooses to drink
    """

    # If user can't drink
    if user["age"] < 21:
        return 0.0

    # If user does drink
    if user["drinking_smoking"]["drinks"]:
        return 1.0

    # User chooses not to drink
    return 0.4
