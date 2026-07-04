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
# HELPERS
# ==========================================================

def print_prompt_stats(prompt: str):

    print()
    print("=" * 80)
    print("PROMPT")
    print("=" * 80)
    print(f"Characters     : {len(prompt):,}")
    print(f"Approx Tokens  : {len(prompt)//4:,}")
    print("=" * 80)


def print_answer(answer: str, generation_time: float):

    print()

    print("=" * 80)
    print("GENERATION")
    print("=" * 80)

    print(f"Completed in   : {generation_time:.2f}s")
    print(f"Characters     : {len(answer):,}")

    print()

    print("=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(answer)


# ==========================================================
# TEXT MODE
# ==========================================================

def run_text_mode():

    question = input("\nQuestion: ").strip()

    if not question:
        return

    print("\nSearching repository...\n")

    retrieval_start = time.time()

    context = retrieve_context(
        question,
        return_string=True,
    )

    retrieval_time = time.time() - retrieval_start

    print(f"\nRepository context : {len(context):,} characters")
    print(f"Retrieval time     : {retrieval_time:.2f}s")

    prompt = build_prompt(
        question=question,
        project_context=context,
    )

    print_prompt_stats(prompt)

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

    generation_time = time.time() - generation_start

    print_answer(
        answer,
        generation_time,
    )


# ==========================================================
# IMAGE MODE
# ==========================================================

def run_image_mode():

    image_path = input("\nImage path: ").strip()

    if not image_path:
        return

    print("\nAnalyzing screenshot...\n")

    vision_start = time.time()

    vision = analyze_image(image_path)

    vision_time = time.time() - vision_start

    print(f"Vision completed in {vision_time:.2f}s")

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

    retrieval_time = time.time() - retrieval_start

    print(f"\nRepository context : {len(context):,} characters")
    print(f"Retrieval time     : {retrieval_time:.2f}s")

    question = """
Implement the uploaded Flutter screen.

The screenshot is the source of truth.

Reuse existing widgets, colors, typography,
spacing and architecture whenever possible.

Generate a complete production-ready Flutter screen.

Always return compilable Flutter code.
"""

    prompt = build_prompt(
        question=question,
        project_context=context,
        vision=vision,
    )

    print_prompt_stats(prompt)

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

    generation_time = time.time() - generation_start

    print_answer(
        answer,
        generation_time,
    )


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

        if mode == "text":
            run_text_mode()

        elif mode == "image":
            run_image_mode()

        else:
            print("\nInvalid mode.\n")


if __name__ == "__main__":
    main()