# ==========================================================
# GENERATOR PROMPT
# ==========================================================

from scripts.models.vision_schema import VisionAnalysis


def build_generator_prompt(
    implementation_plan: str,
    project_context: str,
    flutter_context: str = "",
    vision: VisionAnalysis | None = None,
) -> str:
    """
    Build the code generation prompt.

    The planner has already decided the implementation.
    This prompt focuses only on generating Flutter code.
    """

    vision_section = ""

    if vision:

        vision_section = f"""
SCREEN ANALYSIS

Screen:
{vision.screen}

Theme:
{vision.theme}

Layout:
{vision.layout}

Widgets:
{vision.widgets}

Texts:
{vision.texts}

Actions:
{vision.actions}
"""

    flutter_section = ""

    if flutter_context.strip():

        flutter_section = f"""
FLUTTER DOCUMENTATION

{flutter_context}
"""

    return f"""
You are a senior Flutter engineer.

Generate Flutter code ONLY.

Do NOT explain.

Do NOT justify decisions.

Do NOT redesign the screen.

The implementation plan has already been approved.

Follow it exactly.

==================================================
IMPLEMENTATION PLAN
==================================================

{implementation_plan}

{vision_section}

==================================================
PROJECT CONTEXT
==================================================

Reuse existing widgets whenever possible.

If a reusable widget cannot be used,
replace it with a standard Flutter widget.

{project_context}

{flutter_section}

==================================================
REQUIREMENTS
==================================================

Generate complete, compilable Flutter code.

Always include:

- imports
- StatelessWidget or StatefulWidget
- build()
- helper widgets
- helper methods
- placeholder data where necessary


Never leave empty methods.

Never output pseudocode.

Never omit widget implementations.

If repository code is incomplete,
generate a working Flutter implementation referring to the flutter docs.

==================================================
OUTPUT
==================================================

Return ONLY markdown.

For every file use this format.

### File: lib/path/to/file.dart

```dart
// complete Dart code