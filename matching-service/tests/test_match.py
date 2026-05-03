from matching.event_match import compute_match_score
from tests.data_helpers import make_user, make_event


def fake_user_lookup(user):
    """
    In tests, attendees are already full users
    """
    return user


def test_perfect_match():
    user = make_user(25, ["outdoors", "social"])
    member = make_user(25, ["outdoors", "social"])
    event = make_event(["outdoors", "social"], [member])

    score = compute_match_score(user, event, fake_user_lookup)

    print("Perfect match:", score)
    assert score > 0.8


def test_no_interest_overlap():
    user = make_user(25, ["gaming"])
    member = make_user(25, ["outdoors"])
    event = make_event(["fitness"], [member])

    score = compute_match_score(user, event, fake_user_lookup)

    print("No interest overlap:", score)
    assert score < 0.5


def test_distance_penalty():
    user = make_user(25, ["outdoors"], loc=(0, 0))
    member = make_user(25, ["outdoors"], loc=(0, 0))

    near_event = make_event(["outdoors"], [member], loc=(0, 0))
    far_event = make_event(["outdoors"], [member], loc=(50, 50))

    near_score = compute_match_score(user, near_event, fake_user_lookup)
    far_score = compute_match_score(user, far_event, fake_user_lookup)

    print("Near vs Far:", near_score, far_score)
    assert near_score > far_score


def test_group_similarity():
    user = make_user(25, ["outdoors", "social"])

    similar_member = make_user(26, ["outdoors", "social"])
    different_member = make_user(26, ["gaming"])

    event_good = make_event(["outdoors"], [similar_member])
    event_bad = make_event(["outdoors"], [different_member])

    good_score = compute_match_score(user, event_good, fake_user_lookup)
    bad_score = compute_match_score(user, event_bad, fake_user_lookup)

    print("Group good vs bad:", good_score, bad_score)
    assert good_score > bad_score


def test_age_difference():
    user = make_user(25, ["outdoors"])

    close_age = make_user(27, ["outdoors"])
    far_age = make_user(50, ["outdoors"])

    event_close = make_event(["outdoors"], [close_age])
    event_far = make_event(["outdoors"], [far_age])

    score_close = compute_match_score(user, event_close, fake_user_lookup)
    score_far = compute_match_score(user, event_far, fake_user_lookup)

    print("Age close vs far:", score_close, score_far)
    assert score_close > score_far


def test_size_preference():
    user = make_user(25, ["outdoors"], ranges=[(2, 4)])

    small_event = make_event(["outdoors"], [make_user(25, ["outdoors"])], capacity=3)
    large_event = make_event(["outdoors"], [make_user(25, ["outdoors"])], capacity=10)

    small_score = compute_match_score(user, small_event, fake_user_lookup)
    large_score = compute_match_score(user, large_event, fake_user_lookup)

    print("Size small vs large:", small_score, large_score)
    assert small_score > large_score


def test_extra_user_interests():
    user_simple = make_user(25, ["outdoors", "social"])
    user_extra = make_user(25, ["outdoors", "social", "gaming"])

    member = make_user(25, ["outdoors", "social"])
    event = make_event(["outdoors", "social"], [member])

    score_simple = compute_match_score(user_simple, event, fake_user_lookup)
    score_extra = compute_match_score(user_extra, event, fake_user_lookup)

    print("Simple vs extra interests:", score_simple, score_extra)

    assert score_extra >= score_simple - 0.2


def test_score_bounds():
    user = make_user(25, ["a"])
    member = make_user(30, ["b"])
    event = make_event(["c"], [member])

    score = compute_match_score(user, event, fake_user_lookup)

    print("Bounds:", score)
    assert 0.0 <= score <= 1.0


def test_empty_interests():
    # Meant to check for crashes
    user = make_user(25, [])
    member = make_user(25, [])
    event = make_event([], [member])

    score = compute_match_score(user, event, fake_user_lookup)

    print("Empty interests:", score)
    assert 0.0 <= score <= 1.0


def test_dietary_affects_score():
    user = make_user(25, ["outdoors"], dietary=["vegan"])

    event_good = make_event(
        ["outdoors"], [make_user(25, ["outdoors"])], dining_tags=["vegan"], dining=True
    )

    event_bad = make_event(
        ["outdoors"],
        [make_user(25, ["outdoors"])],
        dining_tags=["pescatarian"],
        dining=True,
    )

    s1 = compute_match_score(user, event_good, fake_user_lookup)
    s2 = compute_match_score(user, event_bad, fake_user_lookup)

    print("Dietary good vs bad:", s1, s2)
    assert s1 > s2


def test_no_dietary_no_penalty():
    user = make_user(25, ["outdoors"], dietary=[])

    event1 = make_event(
        ["outdoors"], [make_user(25, ["outdoors"])], dining_tags=["vegan"], dining=True
    )

    event2 = make_event(
        ["outdoors"],
        [make_user(25, ["outdoors"])],
        dining_tags=["pescatarian"],
        dining=True,
    )

    s1 = compute_match_score(user, event1, fake_user_lookup)
    s2 = compute_match_score(user, event2, fake_user_lookup)

    print("No dietary difference:", s1, s2)
    assert abs(s1 - s2) < 1e-6


def test_empty_dining_tags_penalty():
    user = make_user(25, ["outdoors"], dietary=["vegan"])

    event_with = make_event(
        ["outdoors"], [make_user(25, ["outdoors"])], dining_tags=["vegan"], dining=True
    )

    event_empty = make_event(
        ["outdoors"], [make_user(25, ["outdoors"])], dining_tags=[], dining=True
    )

    s1 = compute_match_score(user, event_with, fake_user_lookup)
    s2 = compute_match_score(user, event_empty, fake_user_lookup)

    print("Dining tags vs empty:", s1, s2)
    assert s1 > s2


def test_underage_drinking_tag_blocked():
    user = make_user(18, ["social"], drinks=False)

    member = make_user(25, ["social", "drinks"], drinks=True)
    event = make_event(["social", "drinks"], [member])

    score = compute_match_score(user, event, fake_user_lookup)

    print("Underage drinking tag:", score)

    assert score == 0.0


def test_non_drinker_penalty():
    user_drinks = make_user(25, ["social"], drinks=True)
    user_no_drink = make_user(25, ["social"], drinks=False)

    member = make_user(25, ["social", "drinks"], drinks=True)
    event = make_event(["social", "drinks"], [member])

    score_drinks = compute_match_score(user_drinks, event, fake_user_lookup)
    score_no_drink = compute_match_score(user_no_drink, event, fake_user_lookup)

    print("Drinker vs non-drinker:", score_drinks, score_no_drink)

    assert score_drinks > score_no_drink
    assert score_no_drink > 0.0


def test_no_drinking_tag_no_penalty():
    user1 = make_user(25, ["social"], drinks=True)
    user2 = make_user(25, ["social"], drinks=False)

    member = make_user(25, ["social"], drinks=True)
    event = make_event(["social"], [member])  # no "drinking" tag

    s1 = compute_match_score(user1, event, fake_user_lookup)
    s2 = compute_match_score(user2, event, fake_user_lookup)

    print("No drinking tag:", s1, s2)

    assert abs(s1 - s2) < 1e-6
