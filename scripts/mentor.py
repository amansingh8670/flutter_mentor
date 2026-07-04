import json
import time

from scripts.llm.chat import generate

from scripts.prompts.prompt_builder import (
    build_prompt,
)

from scripts.retrieval.retrieval import (
    retrieve_context,
    retrieve_multiple_context,
)

from scripts.vision.vision import (
    analyze_image,
)

from scripts.vision.query_builder import (
    build_queries_from_vision,
)


# ==========================================================
# TEXT MODE
# ==========================================================

def run_text_mode():

    question = input("\nQuestion: ").strip()

    print("\nSearching repository...\n")

    retrieval_start = time.time()

    context = retrieve_context(
        question,
        return_string=True,
    )

    print(
        f"\nRepository context: {len(context):,} characters"
    )

    print(
        f"Retrieval completed in "
        f"{time.time() - retrieval_start:.2f}s"
    )

    prompt = build_prompt(
        question=question,
        project_context=context,
    )

    print()
    print("=" * 80)
    print("PROMPT")
    print("=" * 80)
    print(f"Characters : {len(prompt):,}")
    print(f"Approx Tokens : {len(prompt)//4:,}")

    print("\nThinking...\n")

    generation_start = time.time()

    try:

        answer = generate(prompt)

    except Exception as e:

        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print(e)
        return

    print(
        f"\nGeneration completed in "
        f"{time.time() - generation_start:.2f}s"
    )

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


# ==========================================================
# IMAGE MODE
# ==========================================================

def run_image_mode():

    image_path = input("\nImage path: ").strip()

    print("\nAnalyzing screenshot...\n")

    vision_start = time.time()

    vision = analyze_image(image_path)

    print(
        f"Vision completed in "
        f"{time.time() - vision_start:.2f}s"
    )

    print()
    print("=" * 80)
    print("VISION")
    print("=" * 80)

    print(
        json.dumps(
            vision,
            indent=2,
            default=lambda o: getattr(
                o,
                "__dict__",
                str(o),
            ),
        )
    )

    queries = build_queries_from_vision(
        vision
    )

    print()
    print("=" * 80)
    print("RETRIEVAL QUERIES")
    print("=" * 80)

    for query in queries:

        print("-", query)

    print("\nSearching repository...\n")

    retrieval_start = time.time()

    context = retrieve_multiple_context(
        queries
    )

    print(
        f"\nRepository context: {len(context):,} characters"
    )

    print(
        f"Retrieval completed in "
        f"{time.time() - retrieval_start:.2f}s"
    )

    question = """
Implement the uploaded Flutter screen.

The screenshot analysis is the source of truth.

Reuse existing widgets, theme, colors,
typography, navigation and architecture whenever possible.

Generate complete production-ready Flutter code.

Always return a compilable Flutter screen,
even if some reusable widgets are unavailable.
"""

    prompt = build_prompt(
        question=question,
        project_context=context,
        vision=vision,
    )

    print()
    print("=" * 80)
    print("PROMPT")
    print("=" * 80)
    print(f"Characters : {len(prompt):,}")
    print(f"Approx Tokens : {len(prompt)//4:,}")

    print("\nThinking...\n")

    generation_start = time.time()

    try:

        answer = generate(prompt)

    except Exception as e:

        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print(e)
        return

    print(
        f"\nGeneration completed in "
        f"{time.time() - generation_start:.2f}s"
    )

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


# ==========================================================
# MAIN
# ==========================================================

def main():

    while True:

        print()

        mode = input(
            "Mode (text/image/exit): "
        ).strip().lower()

        if mode == "exit":

            break

        elif mode == "text":

            run_text_mode()

        elif mode == "image":

            run_image_mode()

        else:

            print("\nInvalid mode.\n")


if __name__ == "__main__":

    main()