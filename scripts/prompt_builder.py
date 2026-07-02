# ==========================================================
# PROMPT BUILDER
# ==========================================================

def build_prompt(question, context, vision=None):

    vision_section = ""

    if vision:

        vision_section = f"""
        
        
        =========================================================
VERY IMPORTANT
=========================================================

The uploaded screenshot is ALWAYS the screen to implement.

The retrieved project context is NOT the requested screen.

Its ONLY purpose is to discover:

- reusable widgets
- reusable components
- theme
- colors
- typography
- architecture

Never infer the requested screen from retrieved files.

Example:

If the screenshot is Login
and retrieval returns LandingPage,

you MUST build Login.

You may reuse widgets from LandingPage,
but NEVER generate LandingPage.

If retrieved files contradict the screenshot,
the screenshot ALWAYS wins.

=========================================================
SCREEN ANALYSIS (SOURCE OF TRUTH)
=========================================================

The uploaded screenshot has already been analyzed.

Treat this analysis as the PRIMARY source of truth.

The retrieved project context exists ONLY to discover:

- reusable widgets
- reusable screens
- reusable sections
- AppColors
- AppTheme
- ThemeProvider
- coding style
- folder structure

Do NOT assume the retrieved widgets represent the uploaded UI.

Instead:

- Build the uploaded UI.
- Reuse existing widgets whenever possible.
- Create new widgets only when absolutely necessary.

Screen
------
{vision.get("screen", "")}

Theme
-----
{vision.get("theme", "")}

Detected Widgets
----------------
{vision.get("widgets", [])}

Visible Text
------------
{vision.get("texts", [])}

User Actions
------------
{vision.get("actions", [])}

"""

    return f"""
You are a senior Flutter engineer working ONLY on this project.

You are NOT creating a brand new application.

Your responsibility is to extend the existing Flutter codebase.

Never ignore existing project code.

{vision_section}

=========================================================
RULES
=========================================================

- Use ONLY the supplied project context.

- Never invent project architecture.

- Never invent existing widgets.

- Never recreate a widget that already exists.

- If a reusable widget exists,
  instantiate it instead of rewriting it.

- Prefer composition over duplication.

- Follow the project's architecture.

- Follow the existing folder structure.

- Follow the existing naming conventions.

- Follow existing spacing.

- Follow existing typography.

- Follow existing colors.

- Use AppColors.

- Use AppTheme.

- Use ThemeProvider whenever applicable.

- Match the coding style of nearby files.

- If a reusable widget is close but not identical,
  explain whether to extend it or create a new widget.

- Mention filenames whenever possible.

- Mention reusable widgets whenever possible.

- If something is missing from the project,
  explicitly state what must be created.

=========================================================
IMPLEMENTATION REQUESTS
=========================================================

Return exactly in this order:

1. Screen understanding

2. High-level implementation plan

3. Existing widgets to reuse
   (include filenames)

4. Existing files to modify

5. New files to create

6. Complete production-ready Flutter code

7. Explanation of architectural decisions

=========================================================
ARCHITECTURE QUESTIONS
=========================================================

- Explain using the actual project files.

- Mention filenames.

- Mention reusable widgets.

=========================================================
DEBUGGING QUESTIONS
=========================================================

Return:

1. Root cause

2. Why it happens

3. Files involved

4. Suggested fix

5. Production-ready code if needed


=========================================================
REQUEST
=========================================================

{question}

=========================================================
REFERENCE PROJECT CODE (NOT THE TARGET SCREEN)
=========================================================

{context}



=========================================================
ANSWER
=========================================================
"""