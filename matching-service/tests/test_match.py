from app.event_match import compute_match_score

def make_user(age, interests, loc=(0, 0), ranges=[(3, 10)]):
    return {
        "age": age,
        "tags": interests,
        "location": loc,
        "preferred_group_ranges": ranges
    }

def make_event(interests, members, loc=(0, 0), intended_size=6):
    return {
        "tags": interests,
        "location": loc,
        "attendees": members,
        "capacity": intended_size
    }

def test_perfect_match():
    user = make_user(25, ["outdoors", "social"])
    member = make_user(25, ["outdoors", "social"])
    event = make_event(["outdoors", "social"], [member])

    score = compute_match_score(user, event)

    print("Perfect match:", score)
    assert score > 0.8

def test_no_interest_overlap():
    user = make_user(25, ["gaming"])
    member = make_user(25, ["outdoors"])
    event = make_event(["fitness"], [member])

    score = compute_match_score(user, event)

    print("No interest overlap:", score)
    assert score < 0.5

def test_distance_penalty():
    user = make_user(25, ["outdoors"], loc=(0, 0))
    member = make_user(25, ["outdoors"], loc=(0, 0))

    near_event = make_event(["outdoors"], [member], loc=(0, 0))
    far_event = make_event(["outdoors"], [member], loc=(50, 50))

    near_score = compute_match_score(user, near_event)
    far_score = compute_match_score(user, far_event)

    print("Near vs Far:", near_score, far_score)
    assert near_score > far_score

def test_group_similarity():
    user = make_user(25, ["outdoors", "social"])

    similar_member = make_user(26, ["outdoors", "social"])
    different_member = make_user(26, ["gaming"])

    event_good = make_event(["outdoors"], [similar_member])
    event_bad = make_event(["outdoors"], [different_member])

    good_score = compute_match_score(user, event_good)
    bad_score = compute_match_score(user, event_bad)

    print("Group good vs bad:", good_score, bad_score)
    assert good_score > bad_score

def test_age_difference():
    user = make_user(25, ["outdoors"])

    close_age = make_user(27, ["outdoors"])
    far_age = make_user(50, ["outdoors"])

    event_close = make_event(["outdoors"], [close_age])
    event_far = make_event(["outdoors"], [far_age])

    score_close = compute_match_score(user, event_close)
    score_far = compute_match_score(user, event_far)

    print("Age close vs far:", score_close, score_far)
    assert score_close > score_far

def test_size_preference():
    user = make_user(25, ["outdoors"], ranges=[(2, 4)])

    small_event = make_event(["outdoors"], [make_user(25, ["outdoors"])], intended_size=3)
    large_event = make_event(["outdoors"], [make_user(25, ["outdoors"])], intended_size=10)

    small_score = compute_match_score(user, small_event)
    large_score = compute_match_score(user, large_event)

    print("Size small vs large:", small_score, large_score)
    assert small_score > large_score

def test_extra_user_interests():
    user_simple = make_user(25, ["outdoors", "social"])
    user_extra = make_user(25, ["outdoors", "social", "gaming"])

    member = make_user(25, ["outdoors", "social"])
    event = make_event(["outdoors", "social"], [member])

    score_simple = compute_match_score(user_simple, event)
    score_extra = compute_match_score(user_extra, event)

    print("Simple vs extra interests:", score_simple, score_extra)

    assert score_extra >= score_simple - 0.2

def test_score_bounds():
    user = make_user(25, ["a"])
    member = make_user(30, ["b"])
    event = make_event(["c"], [member])

    score = compute_match_score(user, event)

    print("Bounds:", score)
    assert 0.0 <= score <= 1.0

def test_empty_interests():
    # Meant to check for crashes
    user = make_user(25, [])
    member = make_user(25, [])
    event = make_event([], [member])

    score = compute_match_score(user, event)

    print("Empty interests:", score)
    assert 0.0 <= score <= 1.0

