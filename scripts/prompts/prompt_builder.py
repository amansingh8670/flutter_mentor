# ==========================================================
# PROMPT BUILDER
# ==========================================================

from scripts.models.vision_schema import VisionAnalysis


def build_prompt(
    question: str,
    project_context: str,
    flutter_context: str = "",
    vision: VisionAnalysis | None = None,
) -> str:

    vision_section = ""

    if vision:

        vision_section = f"""
=========================================================
PRIMARY SOURCE OF TRUTH
=========================================================

The uploaded screenshot is ALWAYS the UI that must be implemented.

Never infer the requested screen from retrieved repository files.

Repository code is ONLY reference material for discovering:

- reusable widgets
- reusable screens
- reusable sections
- theme
- colors
- typography
- architecture
- coding style

Flutter documentation is ONLY reference material for:

- current Flutter APIs
- latest widgets
- Material 3 patterns
- best practices
- deprecated API replacements

Priority Order

1. Uploaded Screenshot
2. User Request
3. Existing Project Code
4. Flutter Documentation

If these sources disagree,
always follow the higher priority source.

=========================================================
SCREEN ANALYSIS
=========================================================

Screen:
{vision.screen}

Theme:
{vision.theme}

Layout:
{vision.layout}

Widgets:
{vision.widgets}

Visible Text:
{vision.texts}

Actions:
{vision.actions}
"""

    flutter_docs = ""

    if flutter_context.strip():

        flutter_docs = f"""
=========================================================
LATEST FLUTTER DOCUMENTATION
=========================================================

Use this ONLY for:

- latest Flutter APIs
- Material 3
- recommended widgets
- replacement of deprecated APIs
- modern Flutter coding style

{flutter_context}
"""

    return f"""
You are a Staff Flutter Engineer.

You are working inside an EXISTING production Flutter project.

You are extending the project.

You are NOT creating a new architecture.

{vision_section}

=========================================================
PROJECT RULES
=========================================================

Use existing project architecture.

Reuse existing widgets whenever possible.

Never recreate an existing widget.

Instantiate reusable widgets instead.

Reuse:

- AppColors
- AppTheme
- ThemeProvider
- design system
- spacing
- typography

Follow existing:

- folder structure
- naming convention
- coding style

If an exact widget already exists,
instantiate it.

If not,
create a new widget.

Never invent project files.

Never rename existing files.

When creating new widgets,
follow the project's existing patterns.

{flutter_docs}

=========================================================
REQUEST
=========================================================

{question}

=========================================================
PROJECT REFERENCE CODE
=========================================================

This is NOT the requested UI.

It is ONLY reference code to discover reusable components.

{project_context}

=========================================================
RESPONSE FORMAT
=========================================================

Return exactly in this order.

1. Screen Understanding

2. High Level Plan

3. Existing Widgets to Reuse
   - include filenames

4. Existing Files to Modify

5. New Files to Create

6. Flutter Documentation Used
   (only if applicable)

7. Complete Production-Ready Flutter Code

8. Architectural Decisions

=========================================================
ANSWER
=========================================================
"""