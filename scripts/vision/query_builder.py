"""
Build semantic retrieval queries from Vision output.

These queries are later used against:

- Project codebase
- Indexed Flutter documentation

The goal is NOT to describe the screenshot.

The goal is to retrieve reusable Flutter code.
"""

from typing import List, Set, Any

from scripts.models.vision_schema import VisionAnalysis, DetectedWidget, UserAction


# ==========================================================
# NORMALIZATION
# ==========================================================

NORMALIZATION = {
    "login": "login screen",
    "sign in": "login screen",
    "log in": "login screen",

    "signup": "signup screen",
    "sign up": "signup screen",
    "register": "signup screen",

    "textfield": "text field",
    "email": "email text field",
    "password": "password field",

    "button": "primary button",
    "continue": "primary button",

    "app bar": "top app bar",
    "top bar": "top app bar",

    "bottom nav": "bottom navigation",
    "bottom navbar": "bottom navigation",
}


# ==========================================================
# SCREEN KNOWLEDGE
# ==========================================================

SCREEN_HINTS = {
    "login": [
        "authentication",
        "form validation",
        "email text field",
        "password field",
        "primary button",
    ],

    "signup": [
        "authentication",
        "form validation",
        "text field",
        "primary button",
    ],

    "dashboard": [
        "dashboard section",
        "top app bar",
        "bottom navigation",
        "card widget",
    ],

    "home": [
        "top app bar",
        "bottom navigation",
        "section widget",
    ],

    "profile": [
        "profile section",
        "avatar",
    ],

    "settings": [
        "settings tile",
        "switch tile",
    ],

    "recipe": [
        "recipe card",
        "ingredient list",
    ],
}


# ==========================================================
# SAFE EXTRACTION (🔥 FIX)
# ==========================================================

def extract_text(obj: Any) -> str:
    """
    Converts any vision output type into a clean string.
    Handles:
    - str
    - dict
    - DetectedWidget
    - UserAction
    - fallback objects
    """

    if obj is None:
        return ""

    # already string
    if isinstance(obj, str):
        return obj

    # dict from LLM parsing
    if isinstance(obj, dict):
        return (
            obj.get("name")
            or obj.get("text")
            or obj.get("type")
            or ""
        )

    # DetectedWidget dataclass
    if hasattr(obj, "name"):
        return obj.name or ""

    # UserAction dataclass
    if hasattr(obj, "action"):
        return obj.action or ""

    if hasattr(obj, "type"):
        return obj.type or ""

    return str(obj)


# ==========================================================
# NORMALIZATION
# ==========================================================

def normalize(text: str) -> str:
    text = extract_text(text)
    text = text.strip().lower()
    return NORMALIZATION.get(text, text)


# ==========================================================
# ADD QUERY
# ==========================================================

def add(query: Any, queries: List[str], seen: Set[str]):

    query = normalize(query)

    if not query:
        return

    if len(query) < 2:
        return

    if query in seen:
        return

    seen.add(query)
    queries.append(query)


# ==========================================================
# MAIN
# ==========================================================

def build_queries_from_vision(
    vision: VisionAnalysis,
) -> List[str]:

    queries: List[str] = []
    seen: Set[str] = set()

    screen = extract_text(vision.screen).lower()

    # ------------------------------------------------------
    # SCREEN LEVEL
    # ------------------------------------------------------

    if screen:
        add(screen, queries, seen)

        for keyword, hints in SCREEN_HINTS.items():
            if keyword in screen:
                for hint in hints:
                    add(hint, queries, seen)

    # ------------------------------------------------------
    # WIDGETS (FIXED)
    # ------------------------------------------------------

    for widget in vision.widgets:
        add(widget, queries, seen)

    # ------------------------------------------------------
    # USER ACTIONS (FIXED)
    # ------------------------------------------------------

    for action in vision.actions:
        add(action, queries, seen)

    # ------------------------------------------------------
    # TEXTS
    # ------------------------------------------------------

    ignored = {
        "ok",
        "yes",
        "no",
        "cancel",
        "back",
        "next",
    }

    for text in vision.texts:

        text = normalize(text)

        if text in ignored:
            continue

        if len(text) > 40:
            continue

        add(text, queries, seen)

    # ------------------------------------------------------
    # FLUTTER CORE SIGNALS
    # ------------------------------------------------------

    add("AppColors", queries, seen)
    add("AppTheme", queries, seen)
    add("ThemeProvider", queries, seen)

    add("custom widget", queries, seen)
    add("section widget", queries, seen)
    add("reusable component", queries, seen)

    return queries