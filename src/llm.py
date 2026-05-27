"""Thin wrapper around LLM API calls — uses requests directly for speed."""
import requests

# DeepSeek Anthropic-compatible endpoint
DEFAULT_BASE_URL = "https://api.deepseek.com/anthropic"


def call_llm(
    system: str,
    user_message: str,
    api_key: str,
    model: str = "deepseek-chat",
    max_tokens: int = 4096,
    base_url: str | None = None,
    timeout: int = 180,
) -> str:
    """Send a single message to the LLM and return the text response.

    Uses DeepSeek's Anthropic-compatible Messages API when base_url is set,
    otherwise falls back to the native Anthropic SDK.
    """
    url = (base_url or DEFAULT_BASE_URL).rstrip("/") + "/v1/messages"

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user_message}],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }

    resp = requests.post(url, json=body, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    # Extract text, skipping any thinking/reasoning blocks
    for block in data.get("content", []):
        if block.get("type") == "text":
            return block["text"]

    # Fallback: take first block's text if no type filter matched
    if data.get("content"):
        return data["content"][0].get("text", "")

    return ""
