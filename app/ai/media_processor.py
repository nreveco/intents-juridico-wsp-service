"""
app/ai/media_processor.py
Procesamiento de medios con IA local:
  - 🎙️  Audio  → faster-whisper (transcripción local, sin API)
  - 🖼️  Imagen → Ollama Vision (descripción de intención)
  - 📄  PDF    → pypdf (extracción de texto)
"""
import asyncio
import base64
import io
import logging
import os
import tempfile

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# Cliente Ollama para Vision (API compatible con OpenAI)
_vision_client = AsyncOpenAI(
    base_url=settings.ollama_base_url,
    api_key="ollama",
)

# ── Extensiones por MIME para Whisper ──────────────────────────
_AUDIO_EXT: dict[str, str] = {
    "audio/ogg": "ogg",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "mp4",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/aac": "aac",
    "audio/m4a": "m4a",
    "audio/x-m4a": "m4a",
    "audio/webm": "webm",
    "audio/flac": "flac",
}

# ── Mimes aceptados por Vision ──────────────────────────────────
_VISION_MIMES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# ── Modelo faster-whisper (cargado una sola vez, lazy) ──────────
_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            # "base" = buen balance velocidad/calidad para español
            # compute_type="int8" → corre bien en CPU sin GPU
            _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            logger.info("[Whisper] Modelo 'base' cargado en CPU")
        except ImportError:
            logger.error("[Whisper] faster-whisper no instalado — pip install faster-whisper")
            raise
    return _whisper_model


# ──────────────────────────────────────────────────────────────
# Voz → Texto  (faster-whisper local)
# ──────────────────────────────────────────────────────────────

async def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """
    Transcribe un mensaje de voz usando faster-whisper (local, sin API).
    WhatsApp envía audio/ogg;codecs=opus — totalmente soportado.

    Returns:
        Texto transcripto, o "" si falla.
    """
    base_mime = mime_type.split(";")[0].strip().lower()
    ext = _AUDIO_EXT.get(base_mime, "ogg")

    def _transcribe_sync() -> str:
        model = _get_whisper_model()
        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            segments, _ = model.transcribe(tmp_path, language="es")
            return " ".join(s.text for s in segments).strip()
        finally:
            os.unlink(tmp_path)

    try:
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, _transcribe_sync)
        logger.info(f"[Whisper] Transcripción: {text[:80]}{'...' if len(text) > 80 else ''}")
        return text
    except Exception as exc:
        logger.error(f"[Whisper] Error transcribiendo audio: {exc}")
        return ""


# ──────────────────────────────────────────────────────────────
# Imagen → Descripción de intención  (Ollama Vision)
# ──────────────────────────────────────────────────────────────

async def analyze_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    business_name: str = "",
) -> str:
    """
    Analiza una imagen con el modelo vision configurado en Ollama.
    Extrae en una frase qué está consultando el cliente
    para que el intent classifier lo pueda procesar normalmente.

    Returns:
        Descripción de la intención, o "" si falla.
    """
    base_mime = mime_type.split(";")[0].strip().lower()
    if base_mime not in _VISION_MIMES:
        base_mime = "image/jpeg"

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{base_mime};base64,{b64}"

    system_msg = (
        f"Eres el asistente virtual de {business_name or 'un negocio'}. "
        "Un cliente te envió una imagen. Describe en UNA sola oración en español, "
        "en primera persona del cliente, qué está consultando o qué necesita. "
        "Ejemplos: 'Quiero saber el precio de esta pizza.', "
        "'Te mando el comprobante de mi pago.', "
        "'¿Tienen este producto en stock?'"
    )

    try:
        response = await _vision_client.chat.completions.create(
            model=settings.ollama_vision_model,
            messages=[
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url, "detail": "low"},
                        }
                    ],
                },
            ],
            max_tokens=150,
            temperature=0,
        )
        desc = response.choices[0].message.content.strip()
        logger.info(f"[Vision] Descripción imagen: {desc}")
        return desc
    except Exception as exc:
        logger.error(f"[Vision] Error analizando imagen: {exc}")
        return ""


# ──────────────────────────────────────────────────────────────
# PDF → Texto  (pypdf)
# ──────────────────────────────────────────────────────────────

async def extract_pdf_text(pdf_bytes: bytes, max_chars: int = 3000) -> str:
    """
    Extrae texto de un PDF con pypdf (pure Python).
    Retorna los primeros max_chars caracteres.

    Returns:
        Texto del PDF, o "" si vacío / falla.
    """
    try:
        import pypdf  # lazy import: evita ImportError en tiempo de carga
    except ImportError:
        logger.error("[PDF] pypdf no instalado — pip install pypdf")
        return ""

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        pages_text: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text.strip())
        full_text = "\n\n".join(pages_text).strip()
        truncated = full_text[:max_chars]
        logger.info(f"[PDF] {len(reader.pages)} páginas, {len(full_text)} chars extraídos")
        return truncated
    except Exception as exc:
        logger.error(f"[PDF] Error extrayendo texto: {exc}")
        return ""


# ── Extensiones por MIME para Whisper ──────────────────────────
_AUDIO_EXT: dict[str, str] = {
    "audio/ogg": "ogg",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "mp4",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/aac": "aac",
    "audio/m4a": "m4a",
    "audio/x-m4a": "m4a",
    "audio/webm": "webm",
    "audio/flac": "flac",
}

# ── Mimes aceptados por la Vision API ──────────────────────────
_VISION_MIMES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


# ──────────────────────────────────────────────────────────────
# Voz → Texto  (Whisper)
# ──────────────────────────────────────────────────────────────

async def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """
    Transcribe un mensaje de voz usando OpenAI Whisper.
    WhatsApp envía audio/ogg;codecs=opus — totalmente soportado.

    Returns:
        Texto transcripto, o "" si falla.
    """
    base_mime = mime_type.split(";")[0].strip().lower()
    ext = _AUDIO_EXT.get(base_mime, "ogg")

    file_obj = io.BytesIO(audio_bytes)
    file_obj.name = f"audio.{ext}"

    try:
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=file_obj,
            language="es",
        )
        text = response.text.strip()
        logger.info(f"[Whisper] Transcripción: {text[:80]}{'...' if len(text) > 80 else ''}")
        return text
    except Exception as exc:
        logger.error(f"[Whisper] Error transcribiendo audio: {exc}")
        return ""


# ──────────────────────────────────────────────────────────────
# Imagen → Descripción de intención  (GPT-4o Vision)
# ──────────────────────────────────────────────────────────────

async def analyze_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    business_name: str = "",
) -> str:
    """
    Analiza una imagen con GPT-4o Vision.
    Extrae en una frase qué está consultando el cliente
    para que el intent classifier lo pueda procesar normalmente.

    Returns:
        Descripción de la intención, o "" si falla.
    """
    base_mime = mime_type.split(";")[0].strip().lower()
    if base_mime not in _VISION_MIMES:
        base_mime = "image/jpeg"

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{base_mime};base64,{b64}"

    system_msg = (
        f"Eres el asistente virtual de {business_name or 'un negocio'}. "
        "Un cliente te envió una imagen. Describe en UNA sola oración en español, "
        "en primera persona del cliente, qué está consultando o qué necesita. "
        "Ejemplos: 'Quiero saber el precio de esta pizza.', "
        "'Te mando el comprobante de mi pago.', "
        "'¿Tienen este producto en stock?'"
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url, "detail": "low"},
                        }
                    ],
                },
            ],
            max_tokens=150,
            temperature=0,
        )
        desc = response.choices[0].message.content.strip()
        logger.info(f"[Vision] Descripción imagen: {desc}")
        return desc
    except Exception as exc:
        logger.error(f"[Vision] Error analizando imagen: {exc}")
        return ""


# ──────────────────────────────────────────────────────────────
# PDF → Texto  (pypdf)
# ──────────────────────────────────────────────────────────────

async def extract_pdf_text(pdf_bytes: bytes, max_chars: int = 3000) -> str:
    """
    Extrae texto de un PDF con pypdf (pure Python).
    Retorna los primeros max_chars caracteres.

    Returns:
        Texto del PDF, o "" si vacío / falla.
    """
    try:
        import pypdf  # lazy import: evita ImportError en tiempo de carga
    except ImportError:
        logger.error("[PDF] pypdf no instalado — pip install pypdf")
        return ""

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        pages_text: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text.strip())
        full_text = "\n\n".join(pages_text).strip()
        truncated = full_text[:max_chars]
        logger.info(f"[PDF] {len(reader.pages)} páginas, {len(full_text)} chars extraídos")
        return truncated
    except Exception as exc:
        logger.error(f"[PDF] Error extrayendo texto: {exc}")
        return ""
