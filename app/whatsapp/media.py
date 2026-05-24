"""
app/whatsapp/media.py
Descarga archivos multimedia desde Meta Graph API.
- Paso 1: GET /{media_id} → obtiene la URL firmada del archivo
- Paso 2: GET {url}       → descarga el binario
"""
import logging

import httpx

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


async def download_media(whatsapp_token: str, media_id: str) -> tuple[bytes, str]:
    """
    Descarga un archivo multimedia de Meta Graph API.

    Returns:
        (bytes_del_archivo, mime_type)

    Raises:
        httpx.HTTPStatusError si la descarga falla.
    """
    headers = {"Authorization": f"Bearer {whatsapp_token}"}

    async with httpx.AsyncClient(timeout=30) as client:
        # ── Paso 1: obtener URL firmada ─────────────────────────
        meta_resp = await client.get(
            f"{GRAPH_API_BASE}/{media_id}",
            headers=headers,
        )
        meta_resp.raise_for_status()
        meta = meta_resp.json()
        media_url: str = meta["url"]
        mime_type: str = meta.get("mime_type", "application/octet-stream")

        # ── Paso 2: descargar el contenido binario ──────────────
        file_resp = await client.get(media_url, headers=headers)
        file_resp.raise_for_status()

    logger.debug(f"Media {media_id} descargado ({len(file_resp.content)} bytes, {mime_type})")
    return file_resp.content, mime_type
