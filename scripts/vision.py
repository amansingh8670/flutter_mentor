import json
import base64
import requests

CHAT_URL = "http://localhost:11434/api/generate"

MODEL = "qwen2.5vl:3b"


def analyze_image(image_path):

    with open(image_path, "rb") as f:
        image = base64.b64encode(f.read()).decode()

    prompt = """
You are a senior Flutter UI engineer.

Analyze this mobile application screenshot.

Your goal is NOT to generate Flutter code.

Your goal is to describe the screen so another system can search an existing Flutter repository for reusable widgets.

Return ONLY valid JSON.

Schema

{
  "screen": "",
  "theme": "",
  "layout": [],
  "widgets": [],
  "texts": [],
  "colors": [],
  "actions": []
}

--------------------------------------------------

screen

Very short screen name.

Examples

"Login"
"Dashboard"
"Recipe Details"
"Settings"
"Onboarding"

--------------------------------------------------

theme

Return ONLY

"light"

or

"dark"

--------------------------------------------------

layout

Describe major layout regions.

Examples

[
"safe area",
"scroll view",
"column",
"top section",
"bottom sheet",
"bottom navigation",
"floating panel",
"card list"
]

Maximum 8 items.

--------------------------------------------------

widgets

Describe major reusable UI components.

Use semantic names instead of Flutter class names.

Examples

[
"logo",
"profile avatar",
"text field",
"password field",
"search bar",
"checkbox",
"primary button",
"secondary button",
"social login button",
"meal card",
"recipe card",
"nutrition card",
"bottom navigation",
"top app bar",
"floating action button",
"carousel",
"progress bar",
"section header",
"chip",
"tab bar"
]

Do NOT include:

- Email address
- Password
- Login
- Random labels
- Text values

Maximum 15 widgets.

--------------------------------------------------

texts

Return ONLY visible text.

Examples

[
"Welcome Back",
"Sign In",
"Forgot Password?",
"Continue with Google"
]

Do not include placeholder values.

Do not include emails.

Maximum 20 strings.

--------------------------------------------------

colors

Return semantic colors only.

Examples

[
"orange",
"white",
"black",
"grey",
"green",
"red"
]

Never return hex values.

Maximum 8 colors.

--------------------------------------------------

actions

Describe visible user interactions.

Examples

[
"sign in",
"continue with google",
"forgot password",
"toggle remember me",
"scan pantry",
"open notifications",
"view recipe"
]

Maximum 10 actions.

--------------------------------------------------

Rules

- Return ONLY JSON.
- Never explain.
- Never use markdown.
- Never invent hidden UI.
- Ignore status bar.
- Ignore device frame.
- Ignore keyboard.
- Ignore animations.
- Ignore icons unless they represent reusable widgets.
- Prefer reusable sections over tiny details.
- If unsure, return an empty array.

"""

    response = requests.post(
        CHAT_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "images": [image],
            "stream": False
        }
    )

    response.raise_for_status()

    output = response.json()["response"].strip()

    try:
        vision = json.loads(output)

        # Ensure all expected keys exist
        defaults = {
            "screen": "",
            "theme": "",
            "layout": [],
            "widgets": [],
            "texts": [],
            "colors": [],
            "actions": []
        }

        for key, value in defaults.items():
            if key not in vision:
                vision[key] = value

        # Normalize theme
        if isinstance(vision["theme"], str):
            vision["theme"] = vision["theme"].lower()

        return vision

    except json.JSONDecodeError:

        print("\nInvalid JSON returned:\n")
        print(output)

        raise Exception("Vision model did not return valid JSON")