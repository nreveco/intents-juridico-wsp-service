"""
Script temporal para completar el PASO 5:
Reemplaza la función _route_intent en webhook.py con la versión legal.
"""

# Leer el archivo original hasta la línea 334
with open("app/routers/webhook.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Conservar solo hasta la línea 334 (índice 333)
original_content = "".join(lines[:334])

# Nueva función _route_intent para estudio jurídico
new_route_intent = """
# ──────────────────────────────────────────────────────────────
# Intent Router — Estudio Jurídico
# ──────────────────────────────────────────────────────────────

async def _route_intent(
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
    \"\"\"
    Router de intenciones para estudio jurídico.
    Retorna (query_result, interactive_sent).
    \"\"\"
    wa_token = business.whatsapp_token

    # ══════════════════════════════════════════════════════════
    # INTENCIONES MANTENIDAS (útiles para estudio jurídico)
    # ══════════════════════════════════════════════════════════

    if intent == Intent.GREETING:
        msg = business.welcome_message or (
            f"¡Hola! 👋 Somos *{business.name}*, estudio jurídico especializado en "
            "Derecho de Familia. ⚖️\\n\\n"
            "¿En qué podemos ayudarte hoy?"
        )
        return {"default_message": msg}, False

    elif intent == Intent.BOOKING:
        # Agendar consulta con mediador
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
            or getattr(extracted, 'description', None)
            or getattr(extracted, 'legal_matter', None)
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
                msg += f"\\n🗺️ Google Maps: {biz_settings.maps_url}"
            return {"data": {"address": biz_settings.address}, "default_message": msg}, False
        return {"default_message": "📍 Escríbenos y te enviamos la dirección exacta de nuestra oficina."}, False

    elif intent == Intent.HUMAN_SUPPORT:
        # ⚠️ CRÍTICO: Derivar a abogado humano
        result = await handoff.request_human_handoff(
            db=db,
            conversation_id=conversation.id,
            human_support_phone=business.human_support_phone or "",
        )
        
        if business.human_support_phone:
            urgency_note = ""
            if hasattr(extracted, 'is_detained') and extracted.is_detained:
                urgency_note = " ⚠️ URGENTE - Cliente detenido"
            elif hasattr(extracted, 'urgency') and extracted.urgency == "high":
                urgency_note = " ⚠️ URGENTE - Situación crítica"
            
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
        legal_area = getattr(extracted, 'legal_area', None)
        legal_matter = getattr(extracted, 'legal_matter', None)
        description = getattr(extracted, 'description', None) or message_text
        urgency = getattr(extracted, 'urgency', None) or "medium"
        is_detained = getattr(extracted, 'is_detained', None) or False
        
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
            has_prior_record=getattr(extracted, 'has_prior_record', None),
            benefit_type=getattr(extracted, 'benefit_type', None),
        )
        
        # Si es urgente o está detenido, notificar inmediatamente
        if urgency == "high" or is_detained:
            await case_inquiries.notify_urgent_case(
                db=db,
                inquiry_id=inquiry["id"],
                business_id=business.id,
            )
        
        # Buscar servicios relacionados
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
        legal_area = getattr(extracted, 'legal_area', None)
        legal_matter = getattr(extracted, 'legal_matter', None)
        
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
            categories = await legal_services.get_all_legal_categories(
                db=db,
                business_id=business.id
            )
            return {"data": {"categories": categories}}, False
        
        return {"data": {"services": services}}, False

    elif intent == Intent.PAYMENT_INFO:
        # Cliente pregunta por honorarios
        legal_matter = getattr(extracted, 'legal_matter', None)
        
        fee_text = await fee_info.format_fee_info_for_response(
            db=db,
            business_id=business.id,
            legal_matter=legal_matter
        )
        
        return {"default_message": fee_text}, False

    elif intent == Intent.TIMEFRAME_QUERY:
        # Cliente pregunta cuánto demora
        legal_matter = getattr(extracted, 'legal_matter', None)
        
        if legal_matter:
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
                    "default_message": f"⏱️ El proceso de {services[0]['name']} generalmente toma {timeframe}. Los plazos pueden variar según cada caso. ⚖️"
                }, False
        
        return {
            "default_message": (
                "⏱️ Los plazos varían según el tipo de caso y su complejidad. "
                "¿Te gustaría agendar una consulta para una estimación precisa? 📅"
            )
        }, False

    elif intent == Intent.LAWYER_IDENTITY:
        return {
            "default_message": (
                f"👨‍⚖️ Soy el asistente virtual de *{business.name}*. "
                "Estoy aquí para ayudarte y coordinar tu atención con nuestro equipo. ⚖️"
            )
        }, False

    elif intent == Intent.BENEFIT_INFO:
        benefit_type = getattr(extracted, 'benefit_type', None) or "beneficios penitenciarios"
        return {
            "data": {"benefit_type": benefit_type},
            "default_message": (
                f"⚖️ Los {benefit_type} dependen de varios factores. "
                "Necesitamos revisar tu caso específico para asesorarte. "
                "¿Te gustaría agendar una consulta? 📋"
            )
        }, False

    elif intent == Intent.PRIOR_RECORD_QUERY:
        return {
            "default_message": (
                "📋 Los antecedentes previos pueden influir en la estrategia de defensa. "
                "Cada caso es único. ¿Quieres agendar una consulta para revisar tu situación? ⚖️"
            )
        }, False

    else:
        return {
            "default_message": (
                "No entendí bien tu consulta 🤔 Puedo ayudarte con:\\n\\n"
                "⚖️ Información sobre servicios legales\\n"
                "📋 Consultas de casos\\n"
                "💰 Información de honorarios\\n"
                "📅 Agendar consultas\\n"
                "📍 Horarios y ubicación\\n"
                "👨‍⚖️ Hablar con un abogado\\n\\n"
                "¿En qué puedo ayudarte?"
            )
        }, False
"""

# Escribir el archivo completo
with open("app/routers/webhook.py", "w", encoding="utf-8") as f:
    f.write(original_content)
    f.write(new_route_intent)

print("✅ PASO 5 COMPLETADO - webhook.py actualizado con función _route_intent legal")
