"""Minimal DeepSeek JSON client for the two agentic gap notebooks.

The notebooks pass method-specific prompts and payloads. This module only sends
one request, parses one JSON object, validates required top-level keys, and
returns an explicit failure record when the service is unavailable.

Required environment variable
-----------------------------
DEEPSEEK_API_KEY

Optional environment variables
------------------------------
DEEPSEEK_BASE_URL       Default: https://api.deepseek.com
DEEPSEEK_MODELS         Default: deepseek-v4-pro,deepseek-v4-flash
DEEPSEEK_PROXY_URL      Optional HTTP(S) proxy
DEEPSEEK_VERIFY_TLS     Default: true
AGENT_TEMPERATURE       Default: 0.2
AGENT_MAX_TOKENS        Default: 8192
AGENT_TIMEOUT_SECONDS   Default: 240
AGENT_SCHEMA_RETRIES    Default: 2
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Iterable

import httpx

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]


class AgentResponseError(RuntimeError):
    """Raised when a model response is not a valid JSON object."""


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _models() -> list[str]:
    raw = os.getenv("DEEPSEEK_MODELS", "deepseek-v4-pro,deepseek-v4-flash")
    return [item.strip() for item in raw.split(",") if item.strip()]


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return str(value)


def _parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    fenced = re.fullmatch(
        r"```(?:json)?\s*(.*?)\s*```",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if fenced:
        text = fenced.group(1).strip()

    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise AgentResponseError("The model response did not contain a JSON object.")


def _validate_keys(value: dict[str, Any], required_keys: Iterable[str] | None) -> None:
    if not required_keys:
        return
    missing = sorted(set(required_keys).difference(value))
    if missing:
        raise AgentResponseError(
            "The model response is missing: " + ", ".join(missing)
        )


def _failure(reason: str) -> dict[str, Any]:
    return {
        "status": "agent_unavailable",
        "error": reason,
        "_agent": {"provider": "deepseek", "model": None, "successful": False},
    }


def ask_agent(
    system_prompt: str,
    user_payload: Any,
    *,
    action: str = "Running DeepSeek agent",
    required_keys: Iterable[str] | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """Send one strict-JSON request to DeepSeek and return one JSON object."""
    if OpenAI is None:
        return _failure("the openai package is unavailable")

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return _failure("DEEPSEEK_API_KEY is not configured")

    timeout = float(os.getenv("AGENT_TIMEOUT_SECONDS", "240"))
    schema_retries = max(1, int(os.getenv("AGENT_SCHEMA_RETRIES", "2")))
    required = sorted(set(required_keys or []))

    http_options: dict[str, Any] = {
        "timeout": httpx.Timeout(timeout),
        "verify": _env_flag("DEEPSEEK_VERIFY_TLS", True),
    }
    proxy = os.getenv("DEEPSEEK_PROXY_URL")
    if proxy:
        http_options["proxy"] = proxy

    http_client = httpx.Client(**http_options)
    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        http_client=http_client,
    )

    payload_text = json.dumps(
        user_payload,
        ensure_ascii=False,
        default=_json_value,
    )
    schema_instruction = (
        "\n\nReturn JSON only. The top-level object must contain exactly these "
        f"required keys: {', '.join(required)}."
        if required
        else "\n\nReturn JSON only."
    )
    base_messages = [
        {"role": "system", "content": system_prompt + schema_instruction},
        {"role": "user", "content": payload_text},
    ]

    last_error = "unknown error"
    try:
        for model in _models():
            previous_content: str | None = None

            for attempt in range(1, schema_retries + 1):
                try:
                    suffix = (
                        f", schema attempt {attempt}/{schema_retries}"
                        if schema_retries > 1
                        else ""
                    )
                    print(f"{action} ({model}{suffix})...")

                    messages = list(base_messages)
                    if previous_content is not None:
                        messages.extend([
                            {"role": "assistant", "content": previous_content},
                            {
                                "role": "user",
                                "content": (
                                    "Correct the previous response. Return one JSON "
                                    "object only, with every required top-level key. "
                                    "Do not add commentary or Markdown."
                                ),
                            },
                        ])

                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        response_format={"type": "json_object"},
                        extra_body={"thinking": {"type": "disabled"}},
                        temperature=(
                            float(os.getenv("AGENT_TEMPERATURE", "0.0"))
                            if temperature is None
                            else float(temperature)
                        ),
                        max_tokens=(
                            int(os.getenv("AGENT_MAX_TOKENS", "8192"))
                            if max_tokens is None
                            else int(max_tokens)
                        ),
                    )

                    choice = response.choices[0]
                    if choice.finish_reason == "length":
                        raise AgentResponseError(
                            "The JSON response was truncated; increase AGENT_MAX_TOKENS."
                        )

                    # Do not parse reasoning_content as the final JSON response.
                    content = choice.message.content
                    if not content:
                        raise AgentResponseError("The model returned empty content.")

                    previous_content = str(content)
                    result = _parse_json_object(previous_content)

                    try:
                        _validate_keys(result, required)
                    except AgentResponseError as exc:
                        returned = ", ".join(sorted(result)) or "<none>"
                        raise AgentResponseError(
                            f"{exc}; returned top-level keys: {returned}"
                        ) from exc

                    result["_agent"] = {
                        "provider": "deepseek",
                        "model": model,
                        "successful": True,
                        "schema_attempt": attempt,
                    }
                    return result

                except Exception as exc:  # pragma: no cover - remote-dependent
                    last_error = str(exc).strip() or type(exc).__name__
                    print(f"{action} failed with {model}: {last_error}")

    finally:
        http_client.close()

    return _failure(f"all configured models failed: {last_error}")

