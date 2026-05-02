import math
from typing import List, Tuple


def compute_match_score(user, event) -> float:
    """
    Calculates match score between a user and an event.

    user = {
        "age": int,
        "tags": List[str],
        "location": (lat, lon),
        "preferred_group_ranges": List[(min, max)]
    }

    event = {
        "tags": List[str],
        "location": (lat, lon),
        "attendees": List[user],
        "capacity": int
    }
    """

    # Event Score

    interest_event = list_similarity(user["tags"], event["tags"])
    dist_score = distance_score(user["location"], event["location"])

    event_score = (
        0.7 * interest_event +
        0.3 * dist_score
    )

    # Group Score

    members = event["attendees"]

    interest_group = sum(
        list_similarity(user["tags"], m["tags"])
        for m in members
    ) / len(members)

    group_ages = [m["age"] for m in members]
    age_comp = age_score(user["age"], group_ages)

    group_score = (
        0.7 * interest_group +
        0.3 * age_comp
    )

    # Size Score

    intended_size = event.get("capacity", 6)
    ranges = user.get("preferred_group_ranges", [(3, 10)])
    size_score1 = size_score(intended_size, ranges)

    # Final Score

    final_score = 0.3 * event_score + 0.5 * group_score + 0.2 * size_score1

    if event.get("dining", False):
        dietary_multiplier = dietary_score(
            user.get("dietary_restrictions", []),
            event.get("dining_tags", [])
        )
    else:
        dietary_multiplier = 1.0

    final_score *= dietary_multiplier

    return final_score


def list_similarity(a: List[str], b: List[str]) -> float:
    set_a, set_b = set(a), set(b)
    if not set_a and not set_b:
        return 1.0

    intersection = len(set_a & set_b)

    covered = intersection / len(set_a) if set_a else 1.0

    union = len(set_a | set_b)
    overlap = intersection / union if union else 0.0

    return 0.7 * covered + 0.3 * overlap


def haversine_distance_km(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    lat1, lon1 = loc1
    lat2, lon2 = loc2

    R = 6371 #Radius of earth

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2)**2 + \
        math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def distance_score(user_loc, event_loc) -> float:
    d = haversine_distance_km(user_loc, event_loc)
    d = min(d, 50)
    return math.exp(-d / 10)


def distance_to_range(n: int, r_min: int, r_max: int) -> int:
    if r_min <= n <= r_max:
        return 0
    return min(abs(n - r_min), abs(n - r_max))


def size_score(n: int, ranges: List[Tuple[int, int]]) -> float:
    if not ranges:
        return 0.5

    best_distance = min(distance_to_range(n, r[0], r[1]) for r in ranges)
    return math.exp(-best_distance / 3)


def age_score(user_age: int, group_ages: List[int]) -> float:
    mean = sum(group_ages) / len(group_ages)
    variance = sum((a - mean) ** 2 for a in group_ages) / len(group_ages)
    std = math.sqrt(variance)

    return math.exp(-((user_age - mean) ** 2) / (2 * (std ** 2 + 4)))

def dietary_score(user_restrictions, event_dining_tags) -> float:
    """
    Returns a multiplier in [min_penalty, 1.0]

    - 1.0 → fully compatible
    - <1.0 → missing support
    """

    if not user_restrictions:
        return 1.0

    set_u = set(user_restrictions)
    set_e = set(event_dining_tags or [])

    matches = len(set_u & set_e)

    coverage = matches / len(set_u)

    penalty_cap = 0.5

    return penalty_cap + (1 - penalty_cap) * coverage