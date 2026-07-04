"""
Centralized chat interface for Ollama.
"""

import json
import requests

from scripts.config import (
    CHAT_MODEL,
    CHAT_URL,
    LLM_MAX_OUTPUT,
)

# ==========================================================
# CONFIG
# ==========================================================

REQUEST_TIMEOUT = 1800

CONTEXT_SIZE = 8192

MAX_OUTPUT_TOKENS = LLM_MAX_OUTPUT


# ==========================================================
# GENERATE
# ==========================================================

def generate(
    prompt: str,
    system: str | None = None,
    temperature: float = 0.1,
) -> str:

    approx_tokens = len(prompt) // 4

    print()
    print("=" * 80)
    print("LLM REQUEST")
    print("=" * 80)
    print(f"Model          : {CHAT_MODEL}")
    print(f"Prompt chars   : {len(prompt):,}")
    print(f"Approx tokens  : {approx_tokens:,}")
    print(f"Context        : {CONTEXT_SIZE}")
    print(f"Max Output     : {MAX_OUTPUT_TOKENS}")
    print("=" * 80)

    payload = {
        "model": CHAT_MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": temperature,
            "num_ctx": CONTEXT_SIZE,
            "num_predict": MAX_OUTPUT_TOKENS,
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

        response = requests.post(
            CHAT_URL,
            json=payload,
            stream=True,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        parts = []

        print("\nGenerating...\n")

        for line in response.iter_lines():

            if not line:
                continue

            obj = json.loads(line.decode())
            
            print("INSIDE", obj)

            if "response" in obj:

                token = obj["response"]

                print(token, end="", flush=True)

                parts.append(token)

            if obj.get("done", False):
                break

        print()
        print("="*80)
        print("GENERATION")
        print("="*80)

        print("Characters :", len("".join(parts)))
        print("Tokens :", len(parts))
        return "".join(parts).strip()

    except requests.Timeout:

        raise RuntimeError(
            "\nLLM request timed out.\n"
            "Try reducing the prompt size or retrieved context."
        )

    except requests.RequestException as e:

        raise RuntimeError(
            f"\nUnable to contact Ollama.\n\n{e}"
        )


# ==========================================================
# HEALTH CHECK
# ==========================================================

def check_chat_model() -> bool:

    try:

        result = generate(
            "Reply with exactly: OK"
        )

        return result.strip() == "OK"

    except Exception:

        return False


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print()

    print(
        generate(
            "Write exactly three sentences explaining Flutter."
        )
    )