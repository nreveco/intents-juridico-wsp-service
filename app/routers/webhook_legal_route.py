"""
Función _route_intent para estudio jurídico.
Este archivo reemplaza la lógica de routing del webhook.py original.
"""

from app.db.models import Business, BusinessSettings, Conversation
from app.intents.definitions import Intent
from app.services import bookings, handoff, leads, notifications, quotes
from app.services import legal_services, case_inquiries, fee_info
from app.whatsapp.gateway import send_text_message
from sqlalchemy.ext.asyncio import AsyncSession


async def _route_intent_legal(
    intent: Intent,
    extracted,
    business: Business,
    biz_settings,
    db: AsyncSession,
    customer_phone: str,
    customer_name: str,
    conversation: Conversation,
    currency_symbol: str,
    phone_number_id: str,
    message_text: str,
) -> tuple[dict, bool]:
    """
    Router de intenciones para estudio jurídico.
    Retorna (query_result, interactive_sent).
    """
    wa_token = business.whatsapp_token

    # ══════════════════════════════════════════════════════════
    # INTENCIONES MANTENIDAS (útiles para estudio jurídico)
    # ══════════════════════════════════════════════════════════

    if intent == Intent.GREETING:
        msg = business.welcome_message or (
            f"¡Hola! 👋 Somos *{business.name}*, estudio jurídico especializado en "
            "Derecho de Familia y Derecho Civil. ⚖️\n\n"
            "¿En qué podemos ayudarte hoy?"
        )
        return {"default_message": msg}, False

    elif intent == Intent.BOOKING:
        # Agendar consulta con abogado
        if extracted.datetime_requested:
            result = await bookings.create_booking(
                db=db,
                business_id=business.id,
                customer_phone=customer_phone,
                service=extracted.service or "consulta legal",
                datetime_requested=extracted.datetime_requested,
                customer_name=customer_name,
            )
            if result.get("success") and business.human_support_phone:
                data = result["data"]
                await notifications.notify_new_booking(
                    whatsapp_token=wa_token,
                    phone_number_id=phone_number_id,
                    owner_phone=business.human_support_phone,
                    booking_id=data["booking_id"],
                    customer_phone=customer_phone,
                    customer_name=customer_name,
                    service=data["service"],
                    datetime_requested=data["datetime_requested"],
                )
            return result, False
        return {"default_message": "¿Para qué día y hora te gustaría agendar la consulta? 📅"}, False

    elif intent == Intent.QUOTE_REQUEST:
        # Solicitar presupuesto personalizado
        description = (
            extracted.quote_description
            or extracted.description
            or extracted.legal_matter
            or extracted.service
            or message_text
        )
        result = await quotes.create_quote_request(
            db=db,
            business_id=business.id,
            customer_phone=customer_phone,
            description=description,
            customer_name=customer_name,
        )
        if result.get("success") and business.human_support_phone:
            data = result["data"]
            await notifications.notify_new_quote(
                whatsapp_token=wa_token,
                phone_number_id=phone_number_id,
                owner_phone=business.human_support_phone,
                quote_id=data["quote_id"],
                customer_phone=customer_phone,
                customer_name=customer_name,
                description=description,
            )
        return result, False

    elif intent == Intent.HOURS_QUERY:
        # Horarios de atención
        if biz_settings and biz_settings.hours:
            return {"data": {"horarios": biz_settings.hours}}, False
        return {"default_message": "Nuestro horario es de lunes a viernes de 9:00 a 18:00, sábados de 10:00 a 14:00. 🕒"}, False

    elif intent == Intent.LOCATION_QUERY:
        # Dirección de la oficina
        if biz_settings and biz_settings.address:
            msg = f"📍 *Dirección:* {biz_settings.address}"
            if biz_settings.city:
                msg += f", {biz_settings.city}"
            if biz_settings.maps_url:
                msg += f"\n🗺️ Google Maps: {biz_settings.maps_url}"
            return {"data": {"address": biz_settings.address}, "default_message": msg}, False
        return {"default_message": "📍 Escríbenos y te enviamos la dirección exacta de nuestra oficina."}, False

    elif intent == Intent.HUMAN_SUPPORT:
        # ⚠️ CRÍTICO: Derivar a abogado humano
        # Si está detenido o urgencia alta, notificar inmediatamente
        result = await handoff.request_human_handoff(
            db=db,
            conversation_id=conversation.id,
            human_support_phone=business.human_support_phone or "",
        )
        
        if business.human_support_phone:
            urgency_note = ""
            if extracted.is_detained or extracted.urgency == "high":
                urgency_note = " ⚠️ URGENTE - Cliente detenido o situación crítica"
            
            await notifications.notify_handoff(
                whatsapp_token=wa_token,
                phone_number_id=phone_number_id,
                owner_phone=business.human_support_phone,
                customer_phone=customer_phone,
                customer_name=customer_name,
                last_message=f"{message_text}{urgency_note}",
            )
        
        return result, False

    # ══════════════════════════════════════════════════════════
    # NUEVAS INTENCIONES LEGALES
    # ══════════════════════════════════════════════════════════

    elif intent == Intent.CASE_INQUIRY:
        # Cliente consulta si pueden ayudarlo con su caso
        legal_area = extracted.legal_area
        legal_matter = extracted.legal_matter
        description = extracted.description or message_text
        urgency = extracted.urgency or "medium"
        is_detained = extracted.is_detained or False
        
        # Crear consulta de caso
        inquiry = await case_inquiries.create_case_inquiry(
            db=db,
            business_id=business.id,
            customer_phone=customer_phone,
            customer_name=customer_name,
            legal_area=legal_area,
            legal_matter=legal_matter,
            description=description,
            urgency=urgency,
            is_detained=is_detained,
            has_prior_record=extracted.has_prior_record,
            benefit_type=extracted.benefit_type,
        )
        
        # Si es urgente o está detenido, notificar inmediatamente
        if urgency == "high" or is_detained:
            await case_inquiries.notify_urgent_case(
                db=db,
                inquiry_id=inquiry["id"],
                business_id=business.id,
            )
        
        # Buscar servicios relacionados si hay asunto legal
        services_data = []
        if legal_matter:
            services = await legal_services.get_services_by_legal_matter(
                db=db,
                business_id=business.id,
                legal_matter=legal_matter,
                limit=3
            )
            services_data = services
        
        return {
            "data": {
                "inquiry": inquiry,
                "services": services_data,
                "is_urgent": urgency == "high" or is_detained
            }
        }, False

    elif intent == Intent.SERVICE_INFO:
        # Cliente pregunta si ven cierta área legal
        legal_area = extracted.legal_area
        legal_matter = extracted.legal_matter
        
        # Buscar servicios por área o asunto
        if legal_matter:
            services = await legal_services.get_services_by_legal_matter(
                db=db,
                business_id=business.id,
                legal_matter=legal_matter,
                limit=5
            )
        elif legal_area:
            services = await legal_services.search_legal_services(
                db=db,
                business_id=business.id,
                legal_area=legal_area,
                limit=5
            )
        else:
            # Mostrar todas las categorías
            categories = await legal_services.get_all_legal_categories(
                db=db,
                business_id=business.id
            )
            return {"data": {"categories": categories}}, False
        
        return {"data": {"services": services}}, False

    elif intent == Intent.PAYMENT_INFO:
        # Cliente pregunta por honorarios y formas de pago
        legal_matter = extracted.legal_matter
        
        # Formatear información de honorarios
        fee_text = await fee_info.format_fee_info_for_response(
            db=db,
            business_id=business.id,
            legal_matter=legal_matter
        )
        
        return {"default_message": fee_text}, False

    elif intent == Intent.TIMEFRAME_QUERY:
        # Cliente pregunta cuánto demora un proceso
        legal_matter = extracted.legal_matter
        
        if legal_matter:
            # Buscar servicio específico con timeframe
            services = await legal_services.get_services_by_legal_matter(
                db=db,
                business_id=business.id,
                legal_matter=legal_matter,
                limit=1
            )
            if services and services[0].get("estimated_timeframe"):
                timeframe = services[0]["estimated_timeframe"]
                return {
                    "data": {"timeframe": timeframe, "service": services[0]["name"]},
                    "default_message": f"⏱️ El proceso de {services[0]['name']} generalmente toma {timeframe}. Esta es información general. Los plazos pueden variar según las particularidades de cada caso. ⚖️"
                }, False
        
        return {
            "default_message": (
                "⏱️ Los plazos de los procesos legales varían según el tipo de caso y su complejidad. "
                "Para darte una estimación precisa, necesitamos evaluar tu situación específica. "
                "¿Te gustaría agendar una consulta gratuita? 📅"
            )
        }, False

    elif intent == Intent.LAWYER_IDENTITY:
        # Cliente pregunta con quién habla
        return {
            "default_message": (
                f"👨‍⚖️ Soy el asistente virtual de *{business.name}*. "
                "Estoy aquí para responder tus consultas iniciales y coordinar tu atención con nuestro equipo de abogados. "
                "¿En qué más puedo ayudarte? ⚖️"
            )
        }, False

    elif intent == Intent.BENEFIT_INFO:
        # Cliente pregunta por beneficios penitenciarios
        benefit_type = extracted.benefit_type or "beneficios penitenciarios"
        
        return {
            "data": {"benefit_type": benefit_type},
            "default_message": (
                f"⚖️ Los {benefit_type} dependen de varios factores como el tipo de delito, "
                "tiempo cumplido, conducta, antecedentes, entre otros. Esta es información general. "
                "Para evaluar si calificas y asesorarte en el proceso, necesitamos revisar tu caso específico. "
                "¿Te gustaría agendar una consulta con nuestro abogado? 📋"
            )
        }, False

    elif intent == Intent.PRIOR_RECORD_QUERY:
        # Cliente pregunta qué pasa con sus antecedentes previos
        return {
            "default_message": (
                "📋 Tener antecedentes previos puede influir en la estrategia de defensa y las salidas alternativas disponibles, "
                "pero cada caso es único. Necesitamos evaluar tu situación completa para darte una orientación precisa. "
                "Esta es información general. ¿Quieres agendar una consulta para revisar tu caso en detalle? ⚖️"
            )
        }, False

    # ══════════════════════════════════════════════════════════
    # UNKNOWN
    # ══════════════════════════════════════════════════════════

    else:
        return {
            "default_message": (
                "No entendí bien tu consulta 🤔 Puedo ayudarte con:\n\n"
                "⚖️ Información sobre nuestros servicios legales\n"
                "📋 Consultas sobre casos familiares o civiles\n"
                "💰 Información de honorarios\n"
                "📅 Agendar consultas\n"
                "📍 Horarios y ubicación\n"
                "👨‍⚖️ Hablar con un abogado\n\n"
                "¿En qué puedo ayudarte?"
            )
        }, False
