import re


# ==========================================================
# NORMALIZATION
# ==========================================================

NORMALIZATION = {

    # ------------------------------------------------------
    # Text fields
    # ------------------------------------------------------

    "email": "text field",
    "email address": "text field",
    "username": "text field",
    "phone": "text field",

    "password": "password field",

    # ------------------------------------------------------
    # Buttons
    # ------------------------------------------------------

    "sign in": "primary button",
    "login": "primary button",
    "log in": "primary button",

    "sign up": "primary button",
    "register": "primary button",

    "continue": "primary button",

    "sync with google": "google sign in button",
    "continue with google": "google sign in button",
    "google": "google sign in button",

    # ------------------------------------------------------
    # Selection
    # ------------------------------------------------------

    "remember me": "checkbox",

    # ------------------------------------------------------
    # Navigation
    # ------------------------------------------------------

    "back": "back button",

    "top bar": "top app bar",
    "app bar": "top app bar",

    "bottom nav": "bottom navigation",
    "bottom navbar": "bottom navigation",
    "bottom navigation bar": "bottom navigation",

    # ------------------------------------------------------
    # Misc
    # ------------------------------------------------------

    "search": "search bar",
    "search field": "search bar",

    "floating action button": "fab",
}


# ==========================================================
# SCREEN SEMANTICS
# ==========================================================

SCREEN_QUERIES = {

    "login": [
        "authentication",
        "text field",
        "password field",
        "primary button",
        "checkbox",
        "google sign in button"
    ],

    "signup": [
        "authentication",
        "text field",
        "primary button"
    ],

    "register": [
        "authentication",
        "text field",
        "primary button"
    ],

    "dashboard": [
        "top app bar",
        "bottom navigation",
        "card",
        "section"
    ],

    "home": [
        "top app bar",
        "bottom navigation",
        "card"
    ],

    "recipe": [
        "recipe card",
        "meal card"
    ]
}


# ==========================================================
# FILTERS
# ==========================================================

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

HEX_PATTERN = re.compile(
    r"^#?[0-9a-fA-F]{6}$"
)


# ==========================================================
# NORMALIZE
# ==========================================================

def normalize(text):

    text = text.strip().lower()

    return NORMALIZATION.get(
        text,
        text
    )


# ==========================================================
# SHOULD KEEP
# ==========================================================

def should_keep(text):

    if not text:
        return False

    text = text.strip()

    if len(text) < 2:
        return False

    if len(text) > 35:
        return False

    if EMAIL_PATTERN.match(text):
        return False

    if HEX_PATTERN.match(text):
        return False

    return True


# ==========================================================
# ADD UNIQUE
# ==========================================================

def add_query(query, queries, seen):

    query = normalize(query)

    if not should_keep(query):
        return

    if query in seen:
        return

    seen.add(query)

    queries.append(query)


# ==========================================================
# BUILD QUERIES
# ==========================================================

def build_queries_from_vision(vision):

    queries = []

    seen = set()

    # ------------------------------------------------------
    # Screen
    # ------------------------------------------------------

    screen = vision.get("screen", "")

    if screen:

        add_query(
            screen,
            queries,
            seen
        )

        screen_lower = screen.lower()

        for keyword, extra_queries in SCREEN_QUERIES.items():

            if keyword in screen_lower:

                for query in extra_queries:

                    add_query(
                        query,
                        queries,
                        seen
                    )

    # ------------------------------------------------------
    # Theme
    # ------------------------------------------------------

    theme = vision.get("theme", "")

    if theme:

        add_query(
            f"{theme} theme",
            queries,
            seen
        )

    # ------------------------------------------------------
    # Widgets
    # ------------------------------------------------------

    for widget in vision.get("widgets", []):

        add_query(
            widget,
            queries,
            seen
        )

    # ------------------------------------------------------
    # Actions
    # ------------------------------------------------------

    for action in vision.get("actions", []):

        if isinstance(action, dict):

            action = action.get(
                "type",
                ""
            )

        add_query(
            action,
            queries,
            seen
        )

    # ------------------------------------------------------
    # Visible Text
    # ------------------------------------------------------

    ignored = {

        "ok",
        "yes",
        "no",
        "cancel",

        "next",
        "back",

        "continue",

        "submit",

        "sign",

        "in"
    }

    for text in vision.get("texts", []):

        text = normalize(text)

        if text in ignored:
            continue

        add_query(
            text,
            queries,
            seen
        )

    return queries