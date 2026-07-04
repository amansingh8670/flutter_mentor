# ==========================================================
# PLANNER LLM
# ==========================================================

import json
import re

from scripts.llm.chat import generate

from scripts.prompts.planner_prompt import (
    build_planner_prompt,
)

from scripts.models.implementation_plan import (
    ImplementationPlan,
    implementation_plan_from_json,
)

from scripts.models.vision_schema import (
    VisionAnalysis,
)


# ==========================================================
# JSON EXTRACTION
# ==========================================================

def extract_json(text: str) -> dict:
    """
    Extract JSON from LLM response.

    Supports:

    - raw JSON
    - ```json markdown
    - explanations before/after JSON
    """

    text = text.strip()

    match = re.search(
        r"```(?:json)?\s*(.*?)```",
        text,
        re.DOTALL,
    )

    if match:
        text = match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise RuntimeError(
            "Planner did not return JSON."
        )

    text = text[start:end + 1]

    return json.loads(text)


# ==========================================================
# RUN PLANNER
# ==========================================================

def run_planner(
    question: str,
    project_context: str,
    flutter_context: str = "",
    vision: VisionAnalysis | None = None,
) -> ImplementationPlan:

    prompt = build_planner_prompt(
        question=question,
        project_context=project_context,
        flutter_context=flutter_context,
        vision=vision,
    )

    print()
    print("=" * 80)
    print("PLANNER")
    print("=" * 80)
    print(
        f"Prompt Characters : {len(prompt):,}"
    )
    print(
        f"Approx Tokens     : {len(prompt)//4:,}"
    )
    print()

    response = generate(
        prompt=prompt,
        temperature=0.0,
        max_tokens=512,
    )

    if not response.strip():
        raise RuntimeError(
            "Planner returned an empty response."
        )

    try:

        data = extract_json(response)

    except Exception:

        print()
        print("=" * 80)
        print("Planner Raw Response")
        print("=" * 80)
        print(response)

        raise

    plan = implementation_plan_from_json(data)

    print("Planner completed successfully.")

    return plan


# ==========================================================
# DEBUG
# ==========================================================

def print_plan(
    plan: ImplementationPlan,
) -> None:

    print()
    print("=" * 80)
    print("IMPLEMENTATION PLAN")
    print("=" * 80)

    print()

    print("Screen Summary")
    print("-" * 80)
    print(plan.screen_summary)

    print()

    print("Reusable Widgets")
    print("-" * 80)

    for widget in plan.reuse_widgets:

        print(
            f"- {widget.name} "
            f"({widget.file})"
        )

    print()

    print("Files To Modify")
    print("-" * 80)

    for file in plan.modify_files:

        print("-", file)

    print()

    print("Files To Create")
    print("-" * 80)

    for file in plan.new_files:

        print("-", file)

    print()

    print("Architecture Notes")
    print("-" * 80)

    for note in plan.architecture_notes:

        print("-", note)