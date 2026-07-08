import base64
import json
import re

import requests

from scripts.config import (
    CHAT_URL,
    REQUEST_TIMEOUT,
    VISION_MODEL,
)
from scripts.models.vision_schema import VisionAnalysis


# ==========================================================
# PROMPT
# ==========================================================

VISION_PROMPT = """
You are a Senior Flutter UI Architect.

Analyze the screenshot for Flutter code retrieval.

Do NOT generate Flutter code.

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

- Theme must be "light" or "dark"
- Ignore status bar
- Ignore device frame
- Ignore keyboard
- Ignore animations
- Ignore placeholder values
- Ignore passwords
- Ignore email addresses
- Prefer reusable UI sections
- Return semantic widget names
- Return ONLY JSON
"""


# ==========================================================
# HELPERS
# ==========================================================

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image:
        return base64.b64encode(image.read()).decode()



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

    # Remove JS-style comments
    response = re.sub(
        r"//.*?$",
        "",
        response,
        flags=re.MULTILINE,
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

def analyze_image(image_path: str) -> VisionAnalysis:

    image = encode_image(image_path)

    response = requests.post(
        CHAT_URL,
        json={
            "model": VISION_MODEL,
            "prompt": VISION_PROMPT,
            "images": [image],
            "stream": False,
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    output = clean_json(
        data.get("response", "")
    )

    print("=" * 80)
    print("RAW MODEL OUTPUT")
    print("=" * 80)
    print(repr(output))
    print("=" * 80)

    if not output:
        raise RuntimeError(
            f"Vision model '{VISION_MODEL}' returned an empty response.\n\n"
            f"Raw response:\n{json.dumps(data, indent=2)}"
        )

    try:
        parsed = json.loads(output)
        return normalize(parsed)

    except json.JSONDecodeError as e:

        print("\nInvalid Vision JSON\n")
        print(output)

        raise RuntimeError(
            f"Vision model returned invalid JSON.\n\n"
            f"Error: {e}\n\n"
            f"Output:\n{output}"
        ) from e