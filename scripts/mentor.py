import json
import requests

from vision import analyze_image
from retrieval import (
    retrieve_context,
    retrieve_multiple_context
)
from query_builder import (
    build_queries_from_vision
)

CHAT_URL = "http://localhost:11434/api/generate"


# ==========================================================
# FILTER RETRIEVED CONTEXT
# ==========================================================

EXCLUDED_SCREEN_FILES = {
    "landing_page.dart",
    "dashboard_page.dart",
}

EXCLUDED_SCREEN_CHUNKS = {
    "LandingPage",
    "_DashboardPageState",
    "DashboardPage",
}


def filter_context(context, vision):

    if vision is None:
        return context

    screen = vision.get("screen", "").lower()

    # Don't filter if the requested screen actually exists.
    if "landing" in screen or "dashboard" in screen:
        return context

    blocks = context.split("\n\nFILE:")

    kept = []

    for index, block in enumerate(blocks):

        if index == 0:
            current = block
        else:
            current = "FILE:" + block

        lower = current.lower()

        skip = False

        for file in EXCLUDED_SCREEN_FILES:
            if file.lower() in lower:
                skip = True
                break

        if skip:
            continue

        for chunk in EXCLUDED_SCREEN_CHUNKS:
            if f"CHUNK: {chunk}".lower() in lower:
                skip = True
                break

        if skip:
            continue

        kept.append(current)

    # Never return empty context
    if len(kept) < 4:
        return context

    return "\n\n".join(kept)


# ==========================================================
# LLM
# ==========================================================

def ask_llama(question, context, vision=None):

    vision_section = ""

    if vision:

        vision_section = f"""
=========================================================
SCREEN ANALYSIS (SOURCE OF TRUTH)
=========================================================

The uploaded screenshot is ALWAYS the screen to implement.

The retrieved project context exists ONLY to discover:

- reusable widgets
- reusable components
- AppColors
- AppTheme
- ThemeProvider
- typography
- spacing
- architecture

NEVER build a retrieved screen unless it is the same screen detected below.

If retrieval contains LandingPage,
DashboardPage,
RecipePage,
or any unrelated page,

reuse ONLY their widgets.

Do NOT recreate those pages.

=========================================================

Detected Screen:
{vision.get("screen", "")}

Theme:
{vision.get("theme", "")}

Layout:
{json.dumps(vision.get("layout", []), indent=2)}

Widgets:
{json.dumps(vision.get("widgets", []), indent=2)}

Visible Text:
{json.dumps(vision.get("texts", []), indent=2)}

Actions:
{json.dumps(vision.get("actions", []), indent=2)}
"""

    prompt = f"""
You are a senior Flutter engineer working ONLY on this repository.

You are extending an EXISTING Flutter application.

{vision_section}

=========================================================
IMPORTANT
=========================================================

The screenshot is ALWAYS correct.

The retrieved context is ONLY reference material.

Never assume the retrieved page is the requested page.

If the screenshot is Login
and retrieval contains LandingPage,

build Login.

Reuse LandingPage widgets only if appropriate.

Never recreate widgets that already exist.

Reuse:

- AppColors
- AppTheme
- ThemeProvider
- existing typography
- existing spacing
- existing widgets
- existing architecture

If an exact widget already exists,
instantiate it.

If not,
create a new widget.

=========================================================
PROJECT CONTEXT
=========================================================

{context}

=========================================================
REQUEST
=========================================================

{question}

=========================================================
RETURN
=========================================================

Return EXACTLY in this order:

1. Screen understanding

2. Existing widgets to reuse
(include filenames)

3. Existing files to modify

4. New files to create

5. Complete production-ready Flutter code

6. Architectural explanation

Never generate unrelated screens.

Never rewrite existing reusable widgets.
"""

    response = requests.post(
        CHAT_URL,
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["response"]


# ==========================================================
# MAIN
# ==========================================================

while True:

    print()

    mode = input(
        "Mode (text/image/exit): "
    ).strip().lower()

    if mode == "exit":
        break

    vision = None

    if mode == "text":

        question = input("\nQuestion: ")

        print("\nSearching repository...\n")

        context = retrieve_context(
            question,
            n_results=5,
            return_string=True
        )

    elif mode == "image":

        image_path = input("\nImage path: ").strip()

        print("\nAnalyzing screenshot...\n")

        vision = analyze_image(image_path)

        print("=" * 80)
        print("VISION OUTPUT")
        print("=" * 80)
        print(json.dumps(vision, indent=2))

        queries = build_queries_from_vision(vision)

        print()
        print("=" * 80)
        print("SEMANTIC SEARCH QUERIES")
        print("=" * 80)

        for query in queries:
            print("-", query)

        print("\nSearching repository...\n")

        context = retrieve_multiple_context(
            queries,
            n_results_per_query=2
        )

        context = filter_context(
            context,
            vision
        )

        question = """
Implement the uploaded Flutter screen.

The screenshot analysis is the source of truth.

Reuse every existing widget possible.

Reuse AppColors.

Reuse AppTheme.

Reuse ThemeProvider.

Follow existing spacing, typography and architecture.

Create new widgets only when no suitable widget exists.

Generate production-ready Flutter code.

Do NOT implement unrelated retrieved screens.
"""

    else:

        print("\nInvalid mode.\n")
        continue

    print()
    print("=" * 80)
    print("FINAL CONTEXT")
    print("=" * 80)

    print(context[:3000])

    print("\nThinking...\n")

    answer = ask_llama(
        question=question,
        context=context,
        vision=vision
    )

    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)