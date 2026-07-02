"""
llm/chat.py

Centralized chat interface for Ollama.

Every LLM request should go through this file.
"""

import requests

from scripts.config import (
    CHAT_MODEL,
    OLLAMA_BASE_URL,
)


# ==========================================================
# ENDPOINT
# ==========================================================

CHAT_URL = (
    f"{OLLAMA_BASE_URL}/api/generate"
)


# ==========================================================
# GENERATE
# ==========================================================

def generate(
    prompt: str,
    system: str | None = None,
    temperature: float = 0.2,
) -> str:
    """
    Generate a response from the configured chat model.

    Args:
        prompt:
            User prompt.

        system:
            Optional system prompt.

        temperature:
            Sampling temperature.

    Returns:
            Model response.
    """

    payload = {

        "model": CHAT_MODEL,

        "prompt": prompt,

        "stream": False,

        "options": {

            "temperature": temperature,

            "num_ctx": 32768,

            "num_predict": 4096,
        }
    }

    if system:

        payload["system"] = system

    response = requests.post(

        CHAT_URL,

        json=payload,

        timeout=600,
    )

    response.raise_for_status()

    return response.json()["response"]


# ==========================================================
# GENERATE WITH CONTEXT
# ==========================================================

def generate_with_context(
    context: str,
    prompt: str,
    system: str | None = None,
    temperature: float = 0.2,
) -> str:
    """
    Convenience helper for RAG prompts.
    """

    final_prompt = f"""
=========================================================
PROJECT CONTEXT
=========================================================

{context}

=========================================================
REQUEST
=========================================================

{prompt}
"""

    return generate(

        prompt=final_prompt,

        system=system,

        temperature=temperature,
    )


# ==========================================================
# HEALTH CHECK
# ==========================================================

def check_chat_model() -> bool:
    """
    Verify that the configured chat model is available.
    """

    try:

        generate("Reply with only the word OK.")

        return True

    except Exception:

        return False


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("=" * 80)
    print("CHAT MODEL TEST")
    print("=" * 80)

    response = generate(
        "What is Flutter?"
    )

    print(response)