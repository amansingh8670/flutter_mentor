import base64
import json
import re
import requests

from scripts.config import (
    OLLAMA_BASE_URL,
    VISION_MODEL,
    CHAT_URL,
)

from scripts.models.vision_schema import VisionAnalysis


# ==========================================================
# PROMPT
# ==========================================================

VISION_PROMPT = """
You are a Senior Flutter UI Architect.

Your task is NOT to generate Flutter code.

Your task is to analyse this screenshot so another AI can search an existing Flutter repository for reusable widgets.

Return ONLY valid JSON.

Schema:

{
  "screen":"",
  "theme":"",
  "layout":[],
  "widgets":[],
  "texts":[],
  "colors":[],
  "actions":[]
}

Rules

- Keep screen name short.
- Theme must be "light" or "dark".
- Prefer reusable UI sections instead of tiny details.
- Widget names should be semantic.
- Ignore status bar.
- Ignore device frame.
- Ignore keyboard.
- Ignore animations.
- Ignore hidden UI.
- Ignore placeholder values.
- Ignore email addresses.
- Ignore passwords.
- Return semantic colors only.
- Return ONLY JSON.
"""


# ==========================================================
# HELPERS
# ==========================================================

def encode_image(image_path: str) -> str:

    with open(image_path, "rb") as image:
        return base64.b64encode(
            image.read()
        ).decode()


def clean_json(response: str) -> str:

    response = response.strip()

    response = re.sub(
        r"^```json",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"^```",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = response.replace(
        "```",
        "",
    )

    return response.strip()


def normalize(data: dict) -> VisionAnalysis:

    return VisionAnalysis(
        screen=data.get("screen", ""),
        theme=data.get("theme", "").lower(),
        layout=data.get("layout", []),
        widgets=data.get("widgets", []),
        texts=data.get("texts", []),
        colors=data.get("colors", []),
        actions=data.get("actions", []),
    )


# ==========================================================
# MAIN
# ==========================================================

def analyze_image(
    image_path: str,
) -> VisionAnalysis:

    image = encode_image(image_path)

    response = requests.post(
        CHAT_URL,
        json={
            "model": VISION_MODEL,
            "prompt": VISION_PROMPT,
            "images": [image],
            "stream": False,
        },
    )

    response.raise_for_status()

    output = clean_json(
        response.json()["response"]
    )

    try:

        parsed = json.loads(output)

        return normalize(parsed)

    except Exception:

        print("\nInvalid Vision JSON\n")
        print(output)

        raise