# ==========================================================
# PLANNER PROMPT
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
========================================================================
SCREEN ANALYSIS
========================================================================

The uploaded screenshot is the SINGLE SOURCE OF TRUTH.

Screen
------
{vision.screen}

Theme
-----
{vision.theme}

Layout
------
{vision.layout}

Visible Widgets
---------------
{vision.widgets}

Visible Text
------------
{vision.texts}

User Actions
------------
{vision.actions}
"""

    flutter_section = ""

    if flutter_context.strip():

        flutter_section = f"""
========================================================================
FLUTTER DOCUMENTATION
========================================================================

Use only if newer Flutter APIs are required.

{flutter_context}
"""

    return f"""
You are a Staff Flutter Architect.

Your ONLY responsibility is planning.

DO NOT generate Flutter code.

DO NOT generate Dart code.

DO NOT write widgets.

DO NOT explain your reasoning.

DO NOT output markdown.

Return ONLY valid JSON.

========================================================================
OBJECTIVE
========================================================================

Analyze:

1. Screenshot
2. User request
3. Existing project
4. Flutter documentation

Then create a complete implementation plan for another LLM
that will generate the Flutter code.

========================================================================
PRIORITY
========================================================================

1. Uploaded Screenshot
2. User Request
3. Existing Project Code
4. Flutter Documentation

If retrieved code differs from the screenshot,
the screenshot ALWAYS wins.

========================================================================
PROJECT RULES
========================================================================

Reuse existing:

- AppTheme
- AppColors
- ThemeProvider
- Existing reusable widgets
- Existing sections
- Existing components
- Existing navigation

Never rename files.

Never redesign architecture.

Only recommend new widgets if absolutely necessary.

Do not invent project-wide utilities.

========================================================================
SCREEN INFORMATION
========================================================================

{vision_section}

========================================================================
USER REQUEST
========================================================================

{question}

========================================================================
PROJECT CONTEXT
========================================================================

{project_context}

{flutter_section}

========================================================================
YOUR TASK
========================================================================

Determine:

• What this screen is.

• Which widgets should be reused.

• Which files should be modified.

• Which files should be created.

• Widget hierarchy.

• Overall implementation steps.

• Missing reusable components.

• Architecture notes.

• Any assumptions required because of incomplete context.

========================================================================
OUTPUT JSON SCHEMA
========================================================================

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

  "new_files": [
    ""
  ],

  "layout": {{
    "root": "Scaffold",
    "body": [
      {{
        "widget": "",
        "children": [
          {{
            "widget": "",
            "children": []
          }}
        ]
      }}
    ]
  }},

  "architecture_notes": [
    ""
  ],

  "missing_components": [
    ""
  ],

  "implementation_steps": [
    ""
  ],

  "assumptions": [
    ""
  ]
}}

========================================================================
RULES
========================================================================

Return ONLY valid JSON.

No markdown.

No explanations.

No Dart code.

No Flutter code.

No comments.

No additional text before or after the JSON.
""".strip()