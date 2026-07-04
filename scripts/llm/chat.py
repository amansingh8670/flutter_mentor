"""
Centralized chat interface for Ollama.
"""

import requests

from scripts.config import (
    CHAT_MODEL,
    OLLAMA_BASE_URL,
    CHAT_URL,
)

CHAT_URL = CHAT_URL

# ==========================================================
# CONFIG
# ==========================================================

REQUEST_TIMEOUT = 1800  # 30 minutes


# ==========================================================
# GENERATE
# ==========================================================

def generate(
    prompt: str,
    system: str | None = None,
    temperature: float = 0.2,
) -> str:

    approx_tokens = len(prompt) // 4

    print()
    print("=" * 80)
    print("LLM REQUEST")
    print("=" * 80)
    print(f"Model          : {CHAT_MODEL}")
    print(f"Prompt chars   : {len(prompt):,}")
    print(f"Approx tokens  : {approx_tokens:,}")
    print(f"Context        : 8192")
    print(f"Max Output     : 768")
    print("=" * 80)

    payload = {

        "model": CHAT_MODEL,

        "prompt": prompt,

        "stream": True,

        "keep_alive": "30m",

        "options": {
            "temperature": 0.1,
            "num_ctx": 8192,
            "num_predict": 512,
            "repeat_penalty": 1.05,
        },

        # Stop once model reaches the end marker
        "stop": [
            "=========================================================",
            "END OF RESPONSE",
        ],
    }

    if system:
        payload["system"] = system

    try:

        response = requests.post(
            CHAT_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()

    except requests.Timeout:

        raise RuntimeError(
            "\n"
            "LLM request timed out.\n\n"
            "Possible reasons:\n"
            "- Prompt too large\n"
            "- Model generating excessive output\n"
            "- Response format encourages long explanations\n\n"
            "Recommendation:\n"
            "- Reduce retrieved chunks\n"
            "- Reduce prompt size\n"
            "- Limit requested output\n"
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

        response = generate(
            "Reply with exactly one word: OK"
        )

        return response.strip() == "OK"

    except Exception:

        return False


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("=" * 80)
    print("OLLAMA TEST")
    print("=" * 80)

    print(

        generate(

            "Explain Flutter in exactly three sentences."

        )

    )