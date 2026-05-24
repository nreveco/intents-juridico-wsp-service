import logging
from typing import List

from openai import AsyncOpenAI

from app.config import settings
from app.intents.definitions import ExtractedIntent, Intent
from app.prompts.templates import build_intent_prompt

logger = logging.getLogger(__name__)
client = AsyncOpenAI(
    base_url=settings.ollama_base_url,
    api_key="ollama",  # Ollama no requiere API key, pero el SDK lo exige
)


async def classify_intent(
    message: str,
    business_name: str,
    business_type: str,
    categories: List[str],
    conversation_history: List[dict] | None = None,
) -> ExtractedIntent:
    """
    Paso 1 del pipeline.
    Envía el mensaje a Ollama y devuelve la intención + entidades extraídas.
    Usa JSON mode + validación Pydantic (compatible con cualquier modelo Ollama).
    """
    system_prompt = build_intent_prompt(business_name, business_type, categories)

    messages = [{"role": "system", "content": system_prompt}]

    # Incluir últimas 4 interacciones como contexto (ahorra tokens)
    if conversation_history:
        for turn in conversation_history[-4:]:
            messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": message})

    try:
        response = await client.chat.completions.create(
            model=settings.ollama_model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=300,
            temperature=0,
        )
        raw = response.choices[0].message.content
        result = ExtractedIntent.model_validate_json(raw)
        logger.info(f"Intent clasificado: {result.intent.value} | producto={result.product_name}")
        return result
    except Exception as exc:
        logger.warning(f"Error clasificando intent: {exc}")
        return ExtractedIntent(intent=Intent.UNKNOWN)
