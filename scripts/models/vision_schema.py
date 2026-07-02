"""
models/vision_schema.py

Shared models used by the vision pipeline.
"""

from dataclasses import dataclass, field
from typing import List


# ==========================================================
# SCREEN LAYOUT
# ==========================================================

@dataclass(slots=True)
class ScreenLayout:
    """
    High-level layout detected from the screenshot.
    """

    containers: List[str] = field(default_factory=list)

    orientation: str = ""

    scrollable: bool = False


# ==========================================================
# DETECTED WIDGET
# ==========================================================

@dataclass(slots=True)
class DetectedWidget:
    """
    Widget detected from the screenshot.
    """

    name: str

    confidence: float = 1.0

    reusable: bool = True


# ==========================================================
# USER ACTION
# ==========================================================

@dataclass(slots=True)
class UserAction:
    """
    User interaction available on the screen.
    """

    name: str

    widget: str = ""


# ==========================================================
# VISION RESULT
# ==========================================================

@dataclass(slots=True)
class VisionAnalysis:
    """
    Final structured output produced by vision.py
    """

    screen: str = ""

    theme: str = ""

    layout: ScreenLayout = field(
        default_factory=ScreenLayout
    )

    widgets: List[DetectedWidget] = field(
        default_factory=list
    )

    texts: List[str] = field(
        default_factory=list
    )

    colors: List[str] = field(
        default_factory=list
    )

    actions: List[UserAction] = field(
        default_factory=list
    )

    confidence: float = 1.0


# ==========================================================
# SEARCH PLAN
# ==========================================================

@dataclass(slots=True)
class SearchPlan:
    """
    Queries generated from the vision output.
    """

    primary_queries: List[str] = field(
        default_factory=list
    )

    secondary_queries: List[str] = field(
        default_factory=list
    )

    flutter_queries: List[str] = field(
        default_factory=list
    )