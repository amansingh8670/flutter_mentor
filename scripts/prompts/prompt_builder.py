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

    sections = []

    # ======================================================
    # SCREEN ANALYSIS
    # ======================================================

    if vision:

        sections.append(f"""
## SCREEN ANALYSIS

This screenshot is the SINGLE SOURCE OF TRUTH.

Implement exactly this UI.

Screen
{vision.screen}

Theme
{vision.theme}

Layout
{vision.layout}

Widgets
{vision.widgets}

Texts
{vision.texts}

Actions
{vision.actions}
""".strip())

    # ======================================================
    # FLUTTER DOCS
    # ======================================================

    if flutter_context.strip():

        sections.append(f"""
## FLUTTER DOCS

Use ONLY if newer Flutter APIs are required.

{flutter_context}
""".strip())

    # ======================================================
    # FINAL PROMPT
    # ======================================================

    return f"""
You are an expert Flutter engineer.

You are modifying an EXISTING Flutter project.

===========================================================================
PRIORITY
===========================================================================

1. Screenshot
2. User request
3. Existing project code
4. Flutter docs

If repository code conflicts with the screenshot,
follow the screenshot.

===========================================================================
PROJECT RULES
===========================================================================

Reuse existing widgets whenever possible.

Reuse:

- AppTheme
- AppColors
- ThemeProvider
- Design System
- Existing Sections
- Existing Widgets

Never rename existing files.

Never redesign the architecture.

Only create new widgets when required.

===========================================================================
IMPORTANT
===========================================================================

Your goal is to generate a WORKING UI.

Do NOT spend time explaining.

Do NOT describe Flutter concepts.

Do NOT explain architecture.

Do NOT produce long paragraphs.

Generate code quickly.

If a reusable widget is unavailable,
replace it with a normal Flutter widget.

Never stop because context is incomplete.

===========================================================================
SCREEN
===========================================================================

{chr(10).join(sections)}

===========================================================================
USER REQUEST
===========================================================================

{question}

===========================================================================
REFERENCE PROJECT CODE
===========================================================================

Use ONLY if useful.

Ignore unrelated files.

{project_context}

===========================================================================
OUTPUT FORMAT
===========================================================================

Return ONLY these sections.

## Reusable Widgets

• widget names only

## Files To Modify

• filenames only

## Files To Create

• filenames only

## Flutter Code

Generate ONE compilable Dart file.

Requirements:

- imports
- StatelessWidget
- build()
- helper widgets if needed
- placeholder data if required
- no TODOs
- no pseudocode
- no markdown explanations inside code
- maximum 250 lines of Dart

Do NOT explain your code.

Finish immediately after the closing brace of the Dart code.
""".strip()