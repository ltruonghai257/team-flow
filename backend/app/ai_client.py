import litellm

from app.config import settings


def _provider_api_key(model: str) -> tuple[str | None, str | None]:
    normalized = model.strip().lower()

    if normalized.startswith((
        "gpt-",
        "chatgpt-",
        "o1",
        "o3",
        "o4",
        "text-embedding-",
        "tts-",
        "whisper-",
        "dall-e",
    )):
        return settings.OPENAI_API_KEY or None, "OPENAI_API_KEY"

    if normalized.startswith(("claude", "anthropic/")):
        return settings.ANTHROPIC_API_KEY or None, "ANTHROPIC_API_KEY"

    return None, None


async def acompletion(**kwargs):
    model = kwargs.get("model") or settings.AI_MODEL
    api_key, env_var_name = _provider_api_key(str(model))

    if env_var_name and not api_key:
        raise RuntimeError(f"{env_var_name} is required for AI model '{model}'")

    if api_key:
        kwargs["api_key"] = api_key

    return await litellm.acompletion(**kwargs)
