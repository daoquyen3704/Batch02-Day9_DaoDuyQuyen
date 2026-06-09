"""Shared LLM factory for all agents.

Supports multiple OpenAI-compatible providers via environment variables.
Default: OpenRouter. Custom provider: DashScope/OpenAI-compatible mode.
"""

import os

from langchain_openai import ChatOpenAI


def _build_chat_openai(*, model: str, api_key: str, base_url: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0.3,
    )


def get_llm() -> ChatOpenAI:
    """Return a ChatOpenAI client pointed at the configured provider."""
    provider = os.getenv("LLM_PROVIDER", "openrouter").strip().lower()

    if provider == "custom":
        model = os.getenv("CUSTOM_LLM_MODEL") or os.getenv("LLM_MODEL") or "qwen-max"
        api_key = os.getenv("CUSTOM_LLM_API_KEY")
        base_url = os.getenv("CUSTOM_LLM_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
        if not api_key:
            raise ValueError(
                "CUSTOM_LLM_API_KEY is required when LLM_PROVIDER=custom."
            )
        return _build_chat_openai(model=model, api_key=api_key, base_url=base_url)

    model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5")
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is required when LLM_PROVIDER is not custom.")
    return _build_chat_openai(model=model, api_key=api_key, base_url=base_url)
