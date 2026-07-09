from scripts.models.vision_schema import VisionAnalysis


def build_generator_prompt(
    implementation_plan: str,
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
## Flutter Documentation

{flutter_context}
"""

    return f"""
You are an expert Flutter engineer.

Your task is to implement the approved screen.

Do not explain your decisions.
Do not redesign the UI.
Follow the implementation plan exactly.

---

## Implementation Plan

{implementation_plan}

{vision_section}

---

## Existing Project

Implement the UI using standard Flutter widgets and the existing codebase.

{project_context}

{flutter_section}

---

## Requirements

Generate dart code corresponding to the implementation plan.

Every generated file must:
- compile
- not necessary to include imports
- include all required widgets
- contain no omitted implementations

If repository code is incomplete, complete it using Flutter best practices and latest documentation.



---

## Output Format

Return markdown only.

For every generated file use:

### File: lib/path/to/file.dart

```dart
// complete code