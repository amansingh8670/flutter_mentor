"""
Centralized chat interface for Ollama (/api/generate).
"""

import requests

from scripts.config import (
    CHAT_MODEL,
    CHAT_URL,
    LLM_CONTEXT_SIZE,
    LLM_MAX_OUTPUT,
    LLM_TEMPERATURE,
    REQUEST_TIMEOUT,
    KEEP_ALIVE,
)


# ==========================================================
# GENERATE
# ==========================================================

def generate(
    prompt: str,
    system: str | None = None,
    temperature: float = LLM_TEMPERATURE,
) -> str:

    approx_tokens = len(prompt) // 4

    print()
    print("=" * 80)
    print("LLM REQUEST")
    print("=" * 80)
    print(f"Model          : {CHAT_MODEL}")
    print(f"Prompt chars   : {len(prompt):,}")
    print(f"Approx tokens  : {approx_tokens:,}")
    print(f"Context        : {LLM_CONTEXT_SIZE}")
    print(f"Max Output     : {LLM_MAX_OUTPUT}")
    print("=" * 80)

    payload = {
        "model": CHAT_MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": KEEP_ALIVE,
        "options": {
            "temperature": temperature,
            "num_ctx": LLM_CONTEXT_SIZE,
            "num_predict": LLM_MAX_OUTPUT,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.05,
        },
        "stop": [
            "END OF RESPONSE",
        ],
    }

    if system:
        payload["system"] = system

    try:

        print("\nGenerating...\n")

        response = requests.post(
            CHAT_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        output = data.get("response", "").strip()

        print("=" * 80)
        print("GENERATION")
        print("=" * 80)
        print("Characters :", len(output))
        print("Approx Tokens :", len(output) // 4)

        if not output:
            raise RuntimeError(
                f"Model '{CHAT_MODEL}' returned an empty response.\n\n"
                f"Raw response:\n{data}"
            )

        return output

    except requests.Timeout:

        raise RuntimeError(
            "LLM request timed out.\n"
            "Try reducing the prompt size or retrieved context."
        )

    except requests.RequestException as e:

        raise RuntimeError(
            f"Unable to contact Ollama.\n\n{e}"
        )


# ==========================================================
# HEALTH CHECK
# ==========================================================

def check_chat_model() -> bool:

    try:

        result = generate("Reply with exactly: OK")
        return result == "OK"

    except Exception:

        return False


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(
        generate(
            "Write exactly three sentences explaining Flutter."
        )
    )