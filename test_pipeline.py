"""
test_pipeline.py — Prueba el pipeline de intención → acción → respuesta
SIN necesitar WhatsApp ni Meta API. Útil para desarrollo local.

Uso:
    python test_pipeline.py

Requiere:
    - DB corriendo con datos seed (python seed_demo.py)
    - OPENAI_API_KEY en .env
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_intent(message: str, business_name: str = "Fuente de Soda El Rancho"):
    from app.ai.intent_classifier import classify_intent
    from app.ai.response_builder import build_response

    print(f"\n{'─'*50}")
    print(f"📱 Cliente: \"{message}\"")

    extracted = await classify_intent(
        message=message,
        business_name=business_name,
        business_type="restaurant",
        categories=["Completos y Sándwiches", "Hamburguesas", "Bebidas", "Postres"],
    )

    print(f"🧠 Intent: {extracted.intent.value}")
    if extracted.product_name:
        print(f"   Producto: {extracted.product_name}")
    if extracted.quantity:
        print(f"   Cantidad: {extracted.quantity}")
    if extracted.datetime_requested:
        print(f"   Fecha: {extracted.datetime_requested}")

    # Simular resultado del backend para el intent detectado
    mock_result = _mock_backend_result(extracted)

    response = await build_response(
        intent=extracted.intent.value,
        original_message=message,
        query_result=mock_result,
        business_name=business_name,
        currency_symbol="$",
    )

    print(f"🤖 Respuesta: {response}")


def _mock_backend_result(extracted) -> dict:
    from app.intents.definitions import Intent

    intent = extracted.intent

    if intent == Intent.PRICE_QUERY and extracted.product_name:
        if "completo" in extracted.product_name.lower():
            return {"found": True, "data": {"name": "Completo Italiano", "price": 2800, "description": "Con tomate, mayo y palta"}}
        if "hamburguesa" in extracted.product_name.lower():
            return {"found": True, "multiple": True, "data": [
                {"name": "Hamburguesa Clásica", "price": 4500},
                {"name": "Hamburguesa Doble", "price": 5900},
                {"name": "Hamburguesa Pollo Crispy", "price": 4800},
            ]}
        return {"found": False, "data": None, "default_message": f"No encontré '{extracted.product_name}' en nuestro menú."}

    elif intent == Intent.PRODUCT_INFO:
        return {"found": True, "data": {
            "Completos y Sándwiches": [
                {"name": "Completo Italiano", "price": 2800},
                {"name": "Completo Dinámico", "price": 2600},
                {"name": "Completo Doble", "price": 3500},
            ],
            "Hamburguesas": [
                {"name": "Hamburguesa Clásica", "price": 4500},
                {"name": "Hamburguesa Doble", "price": 5900},
            ],
        }}

    elif intent == Intent.ORDER_CREATE:
        return {"success": True, "data": {
            "order_id": "AB12CD34",
            "product": extracted.product_name or "Completo Italiano",
            "quantity": extracted.quantity or 1,
            "total": 2800,
            "status": "pendiente ⏳"
        }}

    elif intent == Intent.BOOKING:
        return {"success": True, "data": {
            "booking_id": "EF56GH78",
            "service": extracted.service or "mesa",
            "datetime_requested": extracted.datetime_requested or "hoy a las 8pm",
            "status": "pendiente de confirmación"
        }}

    elif intent == Intent.HOURS_QUERY:
        return {"data": {"horarios": {
            "lunes a viernes": "09:00-22:00",
            "sábado": "10:00-23:00",
            "domingo": "10:00-21:00",
        }}}

    elif intent == Intent.LOCATION_QUERY:
        return {
            "data": {"address": "Av. Providencia 1234, Local 5"},
            "default_message": "📍 *Dirección:* Av. Providencia 1234, Local 5, Santiago\n🗺️ Google Maps: https://maps.google.com/?q=Av+Providencia+1234+Santiago"
        }

    elif intent == Intent.GREETING:
        return {"default_message": "¡Hola! 👋 Bienvenido a *Fuente de Soda El Rancho*. ¿En qué te ayudo?"}

    elif intent == Intent.HUMAN_SUPPORT:
        return {"default_message": "Entendido, te conecto con uno de nuestros agentes. 👨‍💼\nEn breve te atenderemos. Puedes contactarnos al +56912345678."}

    return {"default_message": "No entendí bien. ¿Puedes reformular tu consulta?"}


async def main():
    print("🧪 Test del Pipeline de Automatización WhatsApp + IA")
    print("=" * 50)

    test_messages = [
        "Hola buenos días",
        "¿Cuánto vale el completo italiano?",
        "¿Tienen hamburguesas? ¿cuánto cuestan?",
        "Quiero pedir un completo dinámico",
        "Quiero reservar una mesa para mañana a las 8pm para 4 personas",
        "¿A qué hora cierran?",
        "¿Dónde están ubicados?",
        "Quiero hablar con alguien, tuve un problema con mi pedido",
        "qiero peedr 2 hamburguesas dobles",  # typo intencional
    ]

    for msg in test_messages:
        await test_intent(msg)

    print(f"\n{'='*50}")
    print("✅ Tests completados")


if __name__ == "__main__":
    asyncio.run(main())
