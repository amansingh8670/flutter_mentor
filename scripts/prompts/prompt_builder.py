# ==========================================================
# PROMPT BUILDER (Gemma Optimized)
# ==========================================================

from scripts.models.vision_schema import VisionAnalysis


def build_prompt(
    question: str,
    project_context: str,
    flutter_context: str = "",
    vision: VisionAnalysis | None = None,
) -> str:

    sections = []

    # ======================================================
    # SCREEN ANALYSIS
    # ======================================================

    if vision:

        sections.append(
            f"""
## Screen Analysis

The uploaded screenshot is the source of truth.

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
""".strip()
        )

    # ======================================================
    # FLUTTER DOCS
    # ======================================================

    if flutter_context.strip():

        sections.append(
            f"""
## Flutter Documentation

Use only when repository context is incomplete or newer Flutter APIs are required.

{flutter_context}
""".strip()
        )

    # ======================================================
    # FINAL PROMPT
    # ======================================================

    return f"""
You are an expert Flutter engineer.

Your task is to implement the requested screen inside an existing Flutter project.

Do not explain your decisions.
Do not redesign the UI.
Generate code only.

--------------------------------------------------

## Priority

1. Screenshot
2. User request
3. Existing project
4. Flutter documentation

If there is any conflict, always follow the screenshot.

--------------------------------------------------

## Existing Project Rules

Prefer reusing existing:

- AppTheme
- AppColors
- ThemeProvider
- reusable widgets
- reusable sections
- shared components
- navigation

Prefer modifying existing files instead of creating new ones.

Only create new widgets when absolutely necessary.

Do not rename existing files.

Do not redesign the project architecture.

--------------------------------------------------

## Screen Information

{chr(10).join(sections)}

--------------------------------------------------

## User Request

{question}

--------------------------------------------------

## Existing Project Context

Use only relevant files.

Ignore unrelated code.

{project_context}

--------------------------------------------------

## Requirements

Generate production-ready Flutter code.

The generated code must:

- compile
- include imports
- include a StatelessWidget or StatefulWidget
- implement build()
- include helper widgets if required
- include placeholder data if necessary
- contain no TODOs
- contain no pseudocode
- complete every widget implementation

If repository code is incomplete, complete it using Flutter best practices.

--------------------------------------------------

## Output Format

Return markdown only.

Use exactly this format.

## Reusable Widgets

- widget names only

## Files To Modify

- file names only

## Files To Create

- file names only

## Flutter Code

Generate ONE complete Dart file.

Maximum 250 lines.

Finish immediately after the closing brace of the Dart code.
""".strip()