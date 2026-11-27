"""Text generation shared by all debate formats. Uses only the standard library."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


KEY_NAMES = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}


def load_keys(path):
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            name, sep, value = line.partition("=")
            name, value = name.strip(), value.strip()
            if sep and name in KEY_NAMES.values() and value:
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                    value = value[1:-1]
                os.environ.setdefault(name, value)


def generate(model, system, message, provider="openai"):
    key_name = KEY_NAMES[provider]
    key = os.environ.get(key_name)
    if not key:
        raise ValueError(f"Set {key_name} in .env or the environment for live mode.")
    payload = {"model": model, "messages": [{"role": "user", "content": message}]}
    headers = {"Content-Type": "application/json"}
    if provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers.update({"x-api-key": key, "anthropic-version": "2023-06-01"})
        payload.update({"system": system, "max_tokens": 2048})
    else:
        url = "https://api.openai.com/v1/chat/completions"
        headers["Authorization"] = f"Bearer {key}"
        payload["messages"].insert(0, {"role": "system", "content": system})
    request = Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers,
    )
    try:
        with urlopen(request, timeout=120) as response:
            result = json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"{provider} returned HTTP {error.code} for model {model}.") from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"{provider} connection failed: {error}") from error
    if provider == "anthropic":
        complete = result["stop_reason"] == "end_turn"
        reply = "\n".join(block["text"] for block in result["content"] if block["type"] == "text")
    else:
        choice = result["choices"][0]
        complete = choice["finish_reason"] == "stop"
        reply = choice["message"]["content"]
    if not complete or not isinstance(reply, str) or not reply.strip():
        raise ValueError(f"Model {model} returned an incomplete or empty turn.")
    return reply.strip()
