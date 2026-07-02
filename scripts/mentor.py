import json

from scripts.llm.chat import generate_with_context

from scripts.prompts.prompt_builder import (
    build_prompt,
)

from scripts.retrieval.retrieval import (
    retrieve_context,
    retrieve_multiple_context,
)

from scripts.retrieval.formatter import (
    format_chunks,
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

    context = retrieve_context(
        question,
        return_string=True,
    )

    prompt = build_prompt(
        question=question,
        context=context,
    )

    print("\nThinking...\n")

    answer = chat(prompt)

    print("\n")
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


# ==========================================================
# IMAGE MODE
# ==========================================================

def run_image_mode():

    image_path = input(
        "\nImage path: "
    ).strip()

    print("\nAnalyzing screenshot...\n")

    vision = analyze_image(image_path)

    print("=" * 80)
    print("VISION")
    print("=" * 80)

    print(
        json.dumps(
            vision,
            indent=2,
            default=lambda o: getattr(o, "__dict__", str(o))
        )
    )

    queries = build_queries_from_vision(
        vision,
    )

    print()
    print("=" * 80)
    print("RETRIEVAL QUERIES")
    print("=" * 80)

    for query in queries:
        print("-", query)

    print("\nSearching repository...\n")

    context = retrieve_multiple_context(
        queries,
    )

    context = format_chunks(
        context=context,
        vision=vision,
    )

    question = """
Implement the uploaded Flutter screen.

The screenshot analysis is the source of truth.

Reuse every existing widget possible.

Reuse AppColors.

Reuse AppTheme.

Reuse ThemeProvider.

Follow existing project architecture.

Create new widgets only if no reusable widget exists.

Generate complete production-ready Flutter code.
"""

    prompt = build_prompt(
        question=question,
        context=context,
        vision=vision,
    )

    print("\nThinking...\n")

    answer = chat(prompt)

    print("\n")
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

        if mode == "text":

            run_text_mode()

        elif mode == "image":

            run_image_mode()

        else:

            print("\nInvalid mode.\n")


if __name__ == "__main__":
    main()