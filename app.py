import os

from flask import Flask, render_template, request, jsonify
from openai import OpenAI, OpenAIError

app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Store latest recommendations
latest_recommendations = ""


def movie_demo_recommendations(interest, preferences, requirements):
    request_details = " ".join((interest, preferences, requirements)).lower()
    asks_for_horror = "horror" in request_details
    asks_for_scifi = any(term in request_details for term in ("sci-fi", "sci fi", "science fiction"))

    if not (asks_for_horror and asks_for_scifi):
        return None

    return """
1. Alien (1979)
Reason: Combines science fiction with tense survival horror aboard a spaceship, matching your request for both genres.

2. The Thing (1982)
Reason: Blends an isolated science-fiction setting with creature horror and suspense.

3. Event Horizon (1997)
Reason: Mixes space exploration and science fiction with supernatural horror.

4. Annihilation (2018)
Reason: Pairs mysterious science fiction with unsettling, atmospheric horror.

5. A Quiet Place (2018)
Reason: Combines a science-fiction premise with suspenseful creature horror.
"""


movie_demo_catalog = [
{
    "title": "Alien (1979)",
    "features": {"space", "creature", "classic", "popular", "intense", "scifi"},
    "year": 1979,
    "popularity": 5,
    "intensity": 5,
    "reason": "Combines science fiction with tense survival horror aboard a spaceship.",
},
{
    "title": "The Thing (1982)",
    "features": {"isolated", "creature", "classic", "popular", "intense", "scifi"},
    "year": 1982,
    "popularity": 4,
    "intensity": 5,
    "reason": "Blends an isolated science-fiction setting with creature horror and suspense.",
},
{
    "title": "Event Horizon (1997)",
    "features": {"space", "psychological", "popular", "intense", "scifi"},
    "year": 1997,
    "popularity": 4,
    "intensity": 5,
    "reason": "Mixes space exploration and science fiction with supernatural horror.",
},
{
    "title": "Annihilation (2018)",
    "features": {"psychological", "atmospheric", "lesser-known", "scifi", "newer"},
    "year": 2018,
    "popularity": 3,
    "intensity": 3,
    "reason": "Pairs mysterious science fiction with unsettling, atmospheric horror.",
},
{
    "title": "A Quiet Place (2018)",
    "features": {"creature", "suspenseful", "popular", "scifi", "newer"},
    "year": 2018,
    "popularity": 5,
    "intensity": 3,
    "reason": "Combines a science-fiction premise with suspenseful creature horror.",
},
{
    "title": "Nope (2022)",
    "features": {"space", "creature", "atmospheric", "lesser-known", "scifi", "newer"},
    "year": 2022,
    "popularity": 3,
    "intensity": 3,
    "reason": "Offers a newer, unusual alien story with science-fiction mystery and horror.",
},
{
    "title": "Signs (2002)",
    "features": {"space", "suspenseful", "popular", "scifi"},
    "year": 2002,
    "popularity": 4,
    "intensity": 2,
    "reason": "Uses an alien-invasion science-fiction premise for suspenseful, less intense horror.",
},
{
    "title": "Sputnik (2020)",
    "features": {"space", "creature", "lesser-known", "scifi", "newer"},
    "year": 2020,
    "popularity": 1,
    "intensity": 4,
    "reason": "A lesser-known sci-fi creature feature about a cosmonaut returning from orbit.",
},
{
    "title": "The Vast of Night (2019)",
    "features": {"space", "atmospheric", "lesser-known", "scifi", "newer"},
    "year": 2019,
    "popularity": 2,
    "intensity": 1,
    "reason": "A quieter, atmospheric alien mystery with a science-fiction focus and mild scares.",
},
{
    "title": "Life (2017)",
    "features": {"space", "creature", "popular", "intense", "scifi", "newer"},
    "year": 2017,
    "popularity": 4,
    "intensity": 4,
    "reason": "A tense space-set creature horror film with a strong science-fiction premise.",
},
]


def refine_movie_demo(feedback):
    words = set(feedback.lower().replace("-", " ").split())
    feature_preferences = {
        "space": {"space", "alien", "aliens", "spaceship", "spacecraft"},
        "creature": {"creature", "monster", "monsters"},
        "psychological": {"psychological", "mind"},
        "atmospheric": {"atmospheric", "slow", "eerie"},
        "suspenseful": {"suspense", "suspenseful", "thriller"},
        "classic": {"classic", "old", "older"},
        "newer": {"new", "newer", "recent", "modern"},
        "lesser-known": {"unknown", "underrated", "obscure", "unpopular"},
    }
    prefer_less_scary = any(
        phrase in feedback.lower()
        for phrase in ("less scary", "not too scary", "less horror", "mild horror", "fewer scares")
    )
    prefer_scarier = any(
        phrase in feedback.lower()
        for phrase in ("scarier", "more scary", "more intense", "more horror")
    )
    prefer_less_popular = any(
        phrase in feedback.lower()
        for phrase in ("less popular", "lesser known", "lesser-known", "underrated", "obscure")
    )
    prefer_newer = any(term in words for term in ("new", "newer", "recent", "modern"))
    prefer_classic = any(term in words for term in ("classic", "old", "older"))

    def score(movie):
        result = sum(
            3 for feature, terms in feature_preferences.items()
            if words.intersection(terms) and feature in movie["features"]
        )
        if prefer_less_scary:
            result += 5 - movie["intensity"]
        if prefer_scarier:
            result += movie["intensity"]
        if prefer_less_popular:
            result += 5 - movie["popularity"]
        if prefer_newer:
            result += movie["year"] // 10
        if prefer_classic:
            result -= movie["year"] // 10
        return result

    selected = sorted(
        movie_demo_catalog,
        key=lambda movie: (score(movie), movie["title"]),
        reverse=True,
    )[:5]
    return "\n\n".join(
        f"{rank}. {movie['title']}\nReason: {movie['reason']}"
        for rank, movie in enumerate(selected, 1)
    )


# -----------------------------------
# HOME PAGE
# -----------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------------
# GENERATE RECOMMENDATIONS
# -----------------------------------

@app.route("/recommend", methods=["POST"])
def recommend():

    global latest_recommendations

    data = request.get_json(silent=True) or {}

    name = data.get("name", "")
    age = data.get("age", "")
    interest = data.get("interest", "")
    preferences = data.get("preferences", "")
    requirements = data.get("requirements", "")

    prompt = f"""
You are Pink Picks, a personalized recommendation system.

User Information:

Name: {name}
Age: {age}
Interest: {interest}
Preferences: {preferences}
Requirements: {requirements}

Generate exactly 5 personalized recommendations.

Treat the user's interest, preferences, and requirements as strict constraints.
Recommend only items in the requested category and satisfy every stated genre
or requirement. Do not substitute a different topic. Rank them from most
suitable to least suitable.

For each recommendation provide:

1. Recommendation name
2. Reason why it is suitable for this user.

Use this format:

1. Recommendation Name
Reason: explanation

2. Recommendation Name
Reason: explanation

3. Recommendation Name
Reason: explanation

4. Recommendation Name
Reason: explanation

5. Recommendation Name
Reason: explanation
"""

    if client is None:
        recommendations = movie_demo_recommendations(interest, preferences, requirements)
        if recommendations is None:
            return jsonify({
                "success": False,
                "error": "Set OPENAI_API_KEY to generate recommendations for this request. The local demo currently supports requests for movies that mix horror and sci-fi."
            }), 503

        latest_recommendations = recommendations
        return jsonify({
            "success": True,
            "recommendations": latest_recommendations,
            "demo": True,
            "notice": "Showing local demo suggestions for your sci-fi and horror movie request. Add an OPENAI_API_KEY for AI-generated recommendations."
        })

    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )
    except OpenAIError:
        app.logger.exception("OpenAI recommendation request failed")
        return jsonify({
            "success": False,
            "error": "The AI recommendation service is unavailable. Please try again shortly."
        }), 502

    latest_recommendations = response.output_text
    return jsonify({
        "success": True,
        "recommendations": latest_recommendations,
        "demo": False
    })


# -----------------------------------
# REFINE RECOMMENDATIONS
# -----------------------------------

@app.route("/refine", methods=["POST"])
def refine():

    global latest_recommendations

    data = request.get_json(silent=True) or {}

    feedback = data.get("feedback", "")

    prompt = f"""
You are Pink Picks, a personalized recommendation system.

Previous recommendations:

{latest_recommendations}

User feedback:

{feedback}

Generate exactly 5 improved recommendations based on
the user's feedback.

Rank them from most suitable to least suitable.

For each recommendation provide:

1. Recommendation name
2. Reason why it matches the updated preferences.

Use this format:

1. Recommendation Name
Reason: explanation

2. Recommendation Name
Reason: explanation

3. Recommendation Name
Reason: explanation

4. Recommendation Name
Reason: explanation

5. Recommendation Name
Reason: explanation
"""

    if client is None:
        if not latest_recommendations:
            return jsonify({
                "success": False,
                "error": "Generate movie recommendations before refining them."
            }), 400

        latest_recommendations = refine_movie_demo(feedback)
        return jsonify({
            "success": True,
            "recommendations": latest_recommendations,
            "demo": True,
            "notice": "These suggestions were locally refined from your feedback. Set OPENAI_API_KEY to use AI refinement."
        })

    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )
    except OpenAIError:
        app.logger.exception("OpenAI refinement request failed")
        return jsonify({
            "success": False,
            "error": "The AI recommendation service is unavailable. Please try again shortly."
        }), 502

    latest_recommendations = response.output_text
    return jsonify({
        "success": True,
        "recommendations": latest_recommendations,
        "demo": False
    })


# -----------------------------------
# START FLASK
# -----------------------------------

if __name__ == "__main__":
    app.run(debug=True)