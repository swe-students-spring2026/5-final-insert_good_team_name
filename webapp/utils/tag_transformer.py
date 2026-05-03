"""Transforms preferences and event types into algorithm tags
List of tags:
outdoors
fitness
social
chill
high_energy
nightlife
drinks
food
games
competitive
casual
creative
learning
music
networking
culture
"""

PREFERENCE_TO_TAGS = {
    "hiking": ["outdoors", "fitness", "chill"],
    "camping": ["outdoors", "chill", "social"],
    "beach": ["outdoors", "chill", "social"],
    "nature_walks": ["outdoors", "chill"],
    "photography": ["creative", "chill"],
    "fishing": ["outdoors", "chill"],
    "gym": ["fitness", "high_energy"],
    "running": ["fitness", "high_energy"],
    "yoga": ["fitness", "chill"],
    "cycling": ["fitness", "outdoors"],
    "basketball": ["fitness", "competitive", "social"],
    "soccer": ["fitness", "competitive", "social"],
    "tennis": ["fitness", "competitive"],
    "martial_arts": ["fitness", "high_energy"],
    "restaurants": ["food", "social"],
    "cooking": ["food", "creative", "chill"],
    "baking": ["food", "creative"],
    "coffee": ["chill", "social"],
    "brunch": ["food", "social", "chill"],
    "wine_tasting": ["drinks", "social", "culture"],
    "bars": ["nightlife", "drinks", "social"],
    "parties": ["nightlife", "high_energy", "social"],
    "dancing": ["nightlife", "high_energy"],
    "clubs": ["nightlife", "high_energy", "drinks"],
    "bar_crawls": ["nightlife", "drinks", "high_energy", "social"],
    "meeting_people": ["social", "networking"],
    "board_games": ["games", "casual", "social"],
    "video_games": ["games", "casual"],
    "esports": ["games", "competitive"],
    "card_games": ["games", "casual"],
    "trivia": ["games", "competitive", "social"],
    "escape_rooms": ["games", "social", "competitive"],
    "painting": ["creative", "chill"],
    "drawing": ["creative", "chill"],
    "writing": ["creative", "chill"],
    "music": ["creative", "music"],
    "singing": ["music", "creative"],
    "dancing_art": ["creative", "music"],
    "crafts": ["creative", "chill"],
    "reading": ["learning", "chill"],
    "studying": ["learning", "casual"],
    "workshops": ["learning", "social"],
    "language_learning": ["learning", "culture"],
    "coding": ["learning"],
    "public_speaking": ["learning", "networking"],
    "networking": ["networking", "social"],
    "entrepreneurship": ["networking", "learning"],
    "startups": ["networking", "learning"],
    "career_events": ["networking", "social"],
    "travel": ["culture", "outdoors"],
    "museums": ["culture", "learning"],
    "theater": ["culture", "creative"],
    "movies": ["casual", "chill"],
    "concerts": ["music", "high_energy", "social"],
    "festivals": ["culture", "social", "high_energy"],
}


EVENT_TYPE_TO_TAGS = {
    "hiking_event": ["outdoors", "fitness", "chill", "social"],
    "beach_day": ["outdoors", "chill", "social"],
    "gym_session": ["fitness", "high_energy"],
    "yoga_class": ["fitness", "chill"],
    "restaurant_meetup": ["food", "social"],
    "coffee_meetup": ["chill", "social"],
    "bar_crawl": ["nightlife", "drinks", "high_energy", "social"],
    "house_party": ["nightlife", "social", "high_energy"],
    "club_night": ["nightlife", "high_energy", "drinks"],
    "board_game_night": ["games", "casual", "social"],
    "trivia_night": ["games", "competitive", "social"],
    "escape_room": ["games", "competitive", "social"],
    "art_session": ["creative", "chill"],
    "writing_group": ["creative", "chill"],
    "music_jam": ["music", "creative", "social"],
    "study_group": ["learning", "casual"],
    "workshop": ["learning", "social"],
    "language_exchange": ["learning", "culture", "social"],
    "networking_event": ["networking", "social"],
    "startup_meetup": ["networking", "learning"],
    "museum_visit": ["culture", "learning"],
    "concert": ["music", "high_energy", "social"],
    "festival": ["culture", "social", "high_energy"],
    "movie_night": ["chill", "casual", "social"],
}


def transform_choices_to_tags(selected_choices, mapping):
    """
    Converts dropdown choices into algorithm tags.
    Example:
    ["hiking", "coffee"] -> ["outdoors", "fitness", "chill", "social"]
    """
    tags = []

    for choice in selected_choices:
        if choice in mapping:
            tags.extend(mapping[choice])

    return list(set(tags))


def transform_preferences_to_tags(preferences):
    return transform_choices_to_tags(preferences, PREFERENCE_TO_TAGS)


def transform_event_types_to_tags(event_types):
    return transform_choices_to_tags(event_types, EVENT_TYPE_TO_TAGS)
