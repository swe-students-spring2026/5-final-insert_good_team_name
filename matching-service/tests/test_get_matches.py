from matching.get_matches import get_ranked_events, get_best_event
from tests.data_helpers import make_user, make_event


# pylint disabled here since this is just a helper for tests
# pylint: disable=too-few-public-methods
class FakeUsersCollection:
    """Fake collection to be used for testing"""

    def __init__(self, users):
        self.users = users

    def find(self, query):
        ids = set(query["_id"]["$in"])

        return [{"_id": uid, **self.users[uid]} for uid in ids if uid in self.users]


user_db = {
    "u1": make_user(25, ["outdoors"]),
    "u2": make_user(25, ["gaming"]),
    "u3": make_user(30, ["fitness"]),
}

users_collection = FakeUsersCollection(user_db)


def test_rank_sorted():
    user = make_user(25, ["outdoors"])

    e1 = make_event(["outdoors"], ["u1"])
    e2 = make_event(["gaming"], ["u2"])
    e3 = make_event(["outdoors", "fitness"], ["u1"])

    ranked = get_ranked_events(user, [e2, e1, e3], users_collection)

    scores = [s for _, s in ranked]

    print("Sorted scores:", scores)
    assert scores == sorted(scores, reverse=True)


def test_best_matches_rank():
    user = make_user(25, ["outdoors"])

    e1 = make_event(["outdoors"], ["u1"])
    e2 = make_event(["gaming"], ["u2"])

    ranked = get_ranked_events(user, [e1, e2], users_collection)
    best_event, best_score = get_best_event(user, [e1, e2], users_collection)

    print("Best vs ranked:", best_score, ranked[0][1])

    assert ranked[0][0] == best_event
    assert abs(ranked[0][1] - best_score) < 1e-6


def test_no_events():
    user = make_user(25, ["outdoors"])

    best_event, best_score = get_best_event(user, [], users_collection)

    print("Empty result:", best_event, best_score)

    assert best_event is None
    assert best_score == 0.0

    ranked = get_ranked_events(user, [], users_collection)
    assert not ranked


def test_single_event():
    user = make_user(25, ["outdoors"])
    event = make_event(["outdoors"], ["u1"])

    best_event, best_score = get_best_event(user, [event], users_collection)
    ranked = get_ranked_events(user, [event], users_collection)

    print("Single:", best_score)

    assert best_event == event
    assert ranked[0][0] == event
    assert abs(ranked[0][1] - best_score) < 1e-6
