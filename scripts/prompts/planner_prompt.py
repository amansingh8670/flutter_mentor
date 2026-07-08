# ==========================================================
# PLANNER PROMPT (Gemma Optimized)
# ==========================================================

from scripts.models.vision_schema import VisionAnalysis


def build_planner_prompt(
    question: str,
    project_context: str,
    flutter_context: str = "",
    vision: VisionAnalysis | None = None,
) -> str:

    vision_section = ""

    if vision:

        vision_section = f"""
## Screen Analysis

Screen:
{vision.screen}

Theme:
{vision.theme}

Layout:
{vision.layout}

Visible Widgets:
{vision.widgets}

Visible Text:
{vision.texts}

User Actions:
{vision.actions}
"""

    flutter_section = ""

    if flutter_context.strip():

        flutter_section = f"""
## Flutter Documentation

Use only when repository context is incomplete or newer Flutter APIs are required.

{flutter_context}
"""

    return f"""
You are an expert Flutter architect.

Your task is to create an implementation plan for another model that will generate the Flutter code.

Return exactly one valid JSON object.

Do not generate Flutter code.
Do not generate Dart code.
Do not explain your reasoning.
Do not output markdown.

--------------------------------------------------

## Priority

1. Screenshot
2. User request
3. Existing project
4. Flutter documentation

If there is any conflict, always follow the screenshot.

--------------------------------------------------

## Project Rules

Prefer reusing existing:

- AppTheme
- AppColors
- ThemeProvider
- reusable widgets
- reusable sections
- navigation
- shared components

Prefer modifying existing files instead of creating new ones.

Only create new widgets when they are clearly required.

Do not redesign the project architecture.

--------------------------------------------------

{vision_section}

--------------------------------------------------

## User Request

{question}

--------------------------------------------------

## Existing Project

{project_context}

{flutter_section}

--------------------------------------------------

## Your Task

Determine:

- what screen should be implemented
- which existing widgets should be reused
- which existing files should be modified
- which new files (if any) must be created
- widget hierarchy
- implementation order

Keep the plan concise and implementation-focused.

--------------------------------------------------

## JSON Schema

{{
  "screen_summary": "",

  "reuse_widgets": [
    {{
      "name": "",
      "file": "",
      "reason": ""
    }}
  ],

  "modify_files": [
    ""
  ],

  "create_files": [
    ""
  ],

  "widget_tree": {{
    "widget": "",
    "children": []
  }},

  "implementation_steps": [
    ""
  ],

  "confidence": "high"
}}

--------------------------------------------------

Rules

- Return ONLY valid JSON.
- No markdown.
- No explanations.
- No comments.
- No text before or after the JSON.
""".strip()