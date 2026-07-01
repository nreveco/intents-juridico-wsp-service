import logging

from openai import AsyncOpenAI

from app.config import settings
from app.prompts.templates import build_response_prompt

logger = logging.getLogger(__name__)
client = AsyncOpenAI(
    base_url=settings.ollama_base_url,
    api_key="ollama",  # Ollama no requiere API key, pero el SDK lo exige
    timeout=30.0,  # Timeout de 30 segundos
    max_retries=0,  # Sin reintentos automáticos
)


async def build_response(
    intent: str,
    original_message: str,
    query_result: dict,
    business_name: str,
    currency_symbol: str = "$",
) -> str:
    """
    Paso 3 del pipeline.
    Recibe los datos REALES del backend y los convierte en una respuesta natural.
    La IA NO inventa — solo formatea lo que el backend encontró.
    """
    # Si el resultado ya tiene un mensaje por defecto y no hay datos, úsalo directo
    if not query_result.get("data") and query_result.get("default_message"):
        return query_result["default_message"]

    system_prompt = build_response_prompt(business_name, currency_symbol)

    user_content = (
        f"Mensaje del cliente: \"{original_message}\"\n"
        f"Intención detectada: {intent}\n"
        f"Datos del sistema: {query_result}"
    )

    logger.info(
        "Calling response builder model",
        extra={
            "intent": intent,
            "query_result_summary": {
                "default_message": bool(query_result.get("default_message")),
                "has_data": bool(query_result.get("data")),
            },
        },
    )

    try:
        response = await client.chat.completions.create(
            model=settings.ollama_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=250,
            temperature=0.4,
        )
        response_text = response.choices[0].message.content.strip()
        logger.info(
            "Response builder completed",
            extra={
                "response_text_preview": response_text[:240],
            },
        )
        return response_text
    except Exception as exc:
        logger.warning(
            "Error construyendo respuesta",
            exc_info=exc,
            extra={
                "intent": intent,
                "query_result_summary": {
                    "default_message": bool(query_result.get("default_message")),
                    "has_data": bool(query_result.get("data")),
                },
            },
        )
        return query_result.get("default_message", "Un momento, te ayudo enseguida. 🙏")
