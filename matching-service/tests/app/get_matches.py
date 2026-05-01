from event_match import compute_match_score

def rank_events_for_user(user, events):
    return sorted(
        [(event, compute_match_score(user, event)) for event in events],
        key=lambda x: x[1],
        reverse=True
    )

def get_best_event_for_user(user, events):
    if not events:
        return None, 0.0

    return max(
        ((event, compute_match_score(user, event)) for event in events),
        key=lambda x: x[1]
    )