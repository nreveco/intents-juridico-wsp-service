# ANÁLISIS DE ADAPTACIÓN PARA ESTUDIO JURÍDICO
## Sistema WhatsApp AI para Mediaciones RJZ

---

## 1. ANÁLISIS DEL CONTEXTO ACTUAL

### 1.1 Sistema Original (Restaurante/Café)
El sistema está diseñado para:
- **Productos físicos** con precio fijo (hamburguesas, bebidas, etc.)
- **Pedidos transaccionales** simples (carrito de compras)
- **Reservas de mesas** con fecha/hora
- **Cotizaciones** para servicios variados
- **Categorías** de productos (Bebidas, Platos, Postres)

### 1.2 Necesidades del Estudio Jurídico RJZ
Según las preguntas frecuentes y delitos consultados:

**PREGUNTAS CLAVE (Top 10):**
1. ¿Cómo son los pagos/honorarios? → **Sistema de cotización personalizado**
2. ¿Pueden hacer algo?/¿Qué podemos hacer? → **Evaluación inicial de caso**
3. ¿Cuánto tiempo demora? → **Información de plazos por tipo de caso**
4. ¿Ven temas penales? → **Filtro de especialidades**
5. ¿Beneficios penitenciarios? → **Asesoría especializada**
6. ¡Hola! Quiero más información → **Flujo de captación desde Instagram**
7. ¿Con quién tengo el gusto? → **Identificación del abogado**
8. ¿Pueden hacer propuesta? → **Sistema de presupuesto**
9. ¿Qué pasa con antecedentes previos? → **Evaluación de riesgo**
10. ¿Pueden coordinar reunión? → **Sistema de agendamiento**

**DELITOS Y MATERIAS MÁS CONSULTADAS:**
1. 🥇 **Tráfico de drogas** (Ley 20.000) — Art. 3°, microtráfico
2. 🥈 **Violencia Intrafamiliar** (VIF) — con peritaje psicosocial
3. 🥉 **Homicidio / Delitos contra las personas**
4. **Casos de familia** (custodia, mediación)
5. **Cobranza judicial**
6. **Traslado de imputados**
7. **Compraventas e inmuebles**
8. **Calumnias e injurias**
9. **Antecedentes penales y prescripción**

---

## 2. MAPEO DE FUNCIONALIDADES

### 2.1 Componentes a MANTENER ✅

| Componente Actual | Uso en Estudio Jurídico |
|---|---|
| **Conversation & Messages** | ✅ Historial de conversaciones con clientes |
| **Lead** | ✅ Registro de potenciales clientes desde Instagram |
| **Booking** | ✅ Agendamiento de reuniones/consultas |
| **Quote + QuoteItem** | ✅ Presupuestos personalizados por caso |
| **HUMAN_SUPPORT** intent | ✅ Derivación a abogado cuando caso es complejo |
| **GREETING** intent | ✅ Bienvenida desde Instagram |
| **HOURS_QUERY** | ✅ Horarios de atención |
| **LOCATION_QUERY** | ✅ Dirección de la oficina |

### 2.2 Componentes a ELIMINAR ❌

| Componente | Razón |
|---|---|
| **Product / Category** | ❌ No hay productos físicos con precio fijo |
| **Order / OrderItem** | ❌ No hay pedidos transaccionales |
| **CART_*** intents (4 intents)** | ❌ No aplica carrito de compras |
| **PRICE_QUERY** | ❌ Los honorarios son variables, no precios fijos |
| **ORDER_CREATE / ORDER_STATUS** | ❌ No hay pedidos, hay casos legales |

### 2.3 Componentes a CREAR 🆕

| Nuevo Componente | Propósito |
|---|---|
| **LegalService** | Servicios legales (Derecho penal, familia, civil, etc.) |
| **LegalCategory** | Categorías de delitos/materias (VIF, drogas, familia, etc.) |
| **CaseType** | Tipos de caso específicos con información base |
| **InitialConsultation** | Registro de consulta inicial del cliente |
| **CaseInquiry** | Consulta de caso con evaluación preliminar |
| **CASE_INQUIRY** intent | Nueva intención: "¿Pueden hacer algo con mi caso?" |
| **SERVICE_INFO** intent | Nueva intención: "¿Ven temas penales/familia?" |
| **TIMEFRAME_QUERY** intent | Nueva intención: "¿Cuánto demora el proceso?" |
| **PAYMENT_INFO** intent | Nueva intención: "¿Cómo son los pagos?" |
| **LAWYER_IDENTITY** intent | Nueva intención: "¿Con quién hablo?" |

---

## 3. NUEVO MODELO DE DATOS

### 3.1 Estructura Propuesta

```python
# ─── Servicios Legales ───────────────────────────────
class LegalCategory(Base):
    """Categorías amplias: Penal, Familia, Civil, Laboral"""
    id, business_id
    name (str)  # "Derecho Penal", "Derecho de Familia"
    description (text)
    icon (str)  # emoji o icono
    is_active (bool)

class LegalService(Base):
    """Servicios específicos dentro de cada categoría"""
    id, business_id, category_id
    name (str)  # "Defensa penal - Ley 20.000"
    description (text)
    typical_duration (str)  # "1-3 meses"
    complexity (str)  # "low" | "medium" | "high"
    base_info (text)  # Info general que el bot puede dar
    requires_evaluation (bool)  # Si requiere eval. personalizada
    is_active (bool)

class CaseType(Base):
    """Tipos de casos con información estructurada"""
    id, business_id, service_id
    name (str)  # "Microtráfico Art. 3", "VIF con lesiones"
    typical_timeframe (str)  # "2-4 meses aprox."
    requires_prison (bool)  # Si típicamente hay prisión preventiva
    typical_penalty (str)  # "541 días a 5 años"
    common_defenses (JSON)  # Lista de estrategias comunes
    documentation_needed (JSON)  # Documentos que se requieren

# ─── Consultas y Casos ───────────────────────────────
class CaseInquiry(Base):
    """Registro de consulta inicial de caso"""
    id, business_id, conversation_id
    customer_phone, customer_name
    inquiry_type (str)  # "case_evaluation" | "general_info"
    legal_matter (str)  # "tráfico de drogas", "VIF"
    description (text)  # Lo que cuenta el cliente
    urgency (str)  # "low" | "medium" | "high"
    has_prior_record (bool)
    is_detained (bool)  # Si está detenido
    status (str)  # "pending" | "evaluated" | "converted_to_quote"
    created_at

class InitialConsultation(Base):
    """Consulta agendada (más formal que Booking)"""
    id, business_id
    customer_phone, customer_name
    inquiry_id (FK to CaseInquiry, nullable)
    datetime_requested (str)
    datetime_confirmed (datetime)
    consultation_type (str)  # "presencial" | "videollamada"
    notes (text)
    status (enum)  # PENDING | CONFIRMED | COMPLETED | CANCELLED
    created_at

# ─── Honorarios y Pagos ──────────────────────────────
class FeeStructure(Base):
    """Estructura de honorarios por tipo de servicio"""
    id, business_id, service_id
    structure_type (str)  # "flat_fee" | "hourly" | "success_fee" | "mixed"
    base_amount (float, nullable)
    hourly_rate (float, nullable)
    success_percentage (float, nullable)
    payment_plans_available (bool)
    typical_payment_plan (str)  # "50% inicial, 50% al finalizar"
    notes (text)
```

### 3.2 Tablas a Mantener (sin cambios)
- ✅ Business
- ✅ BusinessSettings
- ✅ Conversation
- ✅ Message
- ✅ Lead
- ✅ Booking → **renombrar a** `InitialConsultation`
- ✅ Quote + QuoteItem (para presupuestos personalizados)

### 3.3 Tablas a Eliminar
- ❌ Product
- ❌ Category (reemplazar por LegalCategory)
- ❌ Order + OrderItem

---

## 4. NUEVAS INTENCIONES (INTENTS)

### 4.1 Intenciones a MANTENER
```python
✅ GREETING              # "Hola", "Buenos días"
✅ BOOKING               # "Quiero agendar una reunión"
✅ QUOTE_REQUEST         # "Necesito presupuesto"
✅ HUMAN_SUPPORT         # "Quiero hablar con un abogado"
✅ HOURS_QUERY           # "¿A qué hora atienden?"
✅ LOCATION_QUERY        # "¿Dónde están?"
✅ UNKNOWN               # No se entiende
```

### 4.2 Intenciones a ELIMINAR
```python
❌ PRICE_QUERY           # No hay precios fijos
❌ PRODUCT_INFO          # No hay productos
❌ ORDER_CREATE          # No hay pedidos
❌ ORDER_STATUS          # No hay pedidos
❌ CART_ADD              # No hay carrito
❌ CART_VIEW             # No hay carrito
❌ CART_CHECKOUT         # No hay carrito
❌ CART_CLEAR            # No hay carrito
```

### 4.3 Intenciones NUEVAS a CREAR
```python
🆕 CASE_INQUIRY          # "¿Pueden hacer algo?", "¿Qué podemos hacer?"
                         # Extrae: legal_matter, urgency, has_detention

🆕 SERVICE_INFO          # "¿Ven temas penales?", "¿Atienden casos de familia?"
                         # Extrae: legal_area (penal/familia/civil)

🆕 PAYMENT_INFO          # "¿Cómo son los pagos?", "¿Cuánto cobran?"
                         # Extrae: service_type (si mencionó el tipo de caso)

🆕 TIMEFRAME_QUERY       # "¿Cuánto demora?", "¿Cuánto tiempo tarda?"
                         # Extrae: process_type

🆕 LAWYER_IDENTITY       # "¿Con quién hablo?", "¿Quién es usted?"
                         # Sin extracción, respuesta directa

🆕 BENEFIT_INFO          # "¿Puedo salir en libertad condicional?"
                         # Extrae: benefit_type, current_situation

🆕 PRIOR_RECORD_QUERY    # "¿Qué pasa con mis antecedentes previos?"
                         # Extrae: record_type (cumplido/prescrito/vigente)
```

---

## 5. FLUJOS PRINCIPALES REDISEÑADOS

### 5.1 Flujo: Cliente desde Instagram
```
Cliente (Instagram): "¡Hola! Quiero más información"
  → GREETING
  → Respuesta: 
     "¡Hola! Bienvenido a Mediaciones RJZ 👋⚖️
      Somos un estudio jurídico especializado en:
      • Derecho Penal (delitos, defensa, beneficios)
      • Derecho de Familia (VIF, custodia, mediación)
      • Derecho Civil (contratos, cobros, propiedades)
      
      ¿En qué materia legal podemos ayudarte?"
  → Registra Lead en DB
```

### 5.2 Flujo: Consulta de Especialidad
```
Cliente: "¿Ustedes ven temas penales?"
  → SERVICE_INFO (legal_area: "penal")
  → Consulta DB: LegalCategory "Derecho Penal" + servicios
  → Respuesta:
     "Sí, nos especializamos en Derecho Penal ✅
      Atendemos:
      • Ley 20.000 (microtráfico, tráfico)
      • Delitos contra las personas
      • Beneficios penitenciarios
      • Apelaciones y defensas
      
      ¿Tienes un caso específico que consultar?"
```

### 5.3 Flujo: "¿Pueden hacer algo?"
```
Cliente: "Tengo un caso de tráfico de drogas, ¿pueden ayudarme?"
  → CASE_INQUIRY
  → IA extrae: legal_matter="tráfico de drogas", urgency="medium"
  → Crea CaseInquiry en DB (status: pending)
  → Respuesta:
     "Sí, podemos ayudarte con casos de Ley 20.000 ⚖️
      
      Para evaluarte mejor necesito saber:
      • ¿Qué artículo te imputaron? (Art. 3, 4, 5...)
      • ¿Estás detenido actualmente?
      • ¿Tienes antecedentes previos?
      
      O si prefieres, puedes agendar una consulta gratuita."
  → Envía botones: [📅 Agendar] [💬 Seguir consultando]
  → Notifica al abogado: "Nueva consulta de caso: Tráfico de drogas"
```

### 5.4 Flujo: Pregunta de Honorarios
```
Cliente: "¿Cómo son los pagos?"
  → PAYMENT_INFO
  → Consulta DB: FeeStructure (general si no hay caso específico)
  → Respuesta:
     "Nuestros honorarios dependen del tipo de caso y complejidad 💰
      
      Formas de pago:
      • Pago inicial + saldo al finalizar
      • Planes de facilidades disponibles
      • Evaluación gratuita de tu caso
      
      ¿Quieres que te prepare un presupuesto personalizado?"
  → Botones: [✅ Sí, presupuesto] [📅 Agendar reunión]
```

### 5.5 Flujo: Pregunta de Plazos
```
Cliente: "¿Cuánto demora un caso de VIF?"
  → TIMEFRAME_QUERY (process_type: "VIF")
  → Consulta DB: CaseType.typical_timeframe donde name LIKE "%VIF%"
  → Respuesta:
     "Los casos de VIF generalmente toman 2-4 meses ⏱️
      
      Etapas:
      1. Denuncia y cautelares (días)
      2. Investigación (1-2 meses)
      3. Audiencia preparatoria
      4. Juicio o acuerdo
      
      El tiempo real depende de la complejidad.
      ¿Te gustaría agendar una evaluación de tu caso?"
```

### 5.6 Flujo: Agendamiento (MANTENER)
```
Cliente: "Quiero agendar una reunión"
  → BOOKING
  → Crea InitialConsultation (ex-Booking) en DB
  → Respuesta:
     "📅 Perfecto, coordinemos tu consulta.
      
      ¿Qué día y hora te acomoda?
      Atendemos de lunes a viernes, 9:00-18:00"
  → Cliente responde fecha
  → Confirma y notifica al abogado
```

---

## 6. ADAPTACIONES EN PROMPTS

### 6.1 Prompt de Clasificación (intent_classifier)

**ACTUAL (Restaurante):**
```
"Categorías del negocio disponibles: Bebidas, Platos, Postres"
"PRICE_QUERY: cliente pregunta por precio"
"ORDER_CREATE: cliente quiere hacer pedido"
```

**NUEVO (Estudio Jurídico):**
```
"Áreas legales disponibles: Derecho Penal, Derecho de Familia, Derecho Civil"
"CASE_INQUIRY: cliente consulta si pueden ayudarlo con un caso legal"
"SERVICE_INFO: cliente pregunta si atienden cierta materia legal"
"PAYMENT_INFO: cliente pregunta por honorarios o formas de pago"
"TIMEFRAME_QUERY: cliente pregunta cuánto demora un proceso"
```

### 6.2 Prompt de Respuesta (response_builder)

**ACTUAL:**
```
"Responde de forma natural y amigable"
"Usa los DATOS REALES - nunca inventes precios"
"Los precios son en $ (pesos chilenos)"
```

**NUEVO:**
```
"Eres el asistente virtual de Mediaciones RJZ, estudio jurídico especializado"
"Tono: profesional pero cercano, empático con situaciones legales"
"NUNCA des asesoría legal definitiva - siempre sugiere consulta con abogado"
"Usa emojis legales: ⚖️ 📋 👨‍⚖️ (con moderación)"
"Si el caso es complejo o urgente, deriva inmediatamente a abogado humano"
```

---

## 7. SEED DATA PARA MEDIACIONES RJZ

### 7.1 Business
```python
name: "Mediaciones RJZ"
business_type: "LAW_FIRM"  # NUEVO tipo
welcome_message: """
¡Hola! Bienvenido a *Mediaciones RJZ* ⚖️

Somos un estudio jurídico especializado en:
• Derecho Penal (defensa, beneficios)
• Derecho de Familia (VIF, custodia)
• Derecho Civil (contratos, cobros)

¿En qué podemos ayudarte hoy?
"""
human_support_phone: "+56912345678"  # Número del abogado
```

### 7.2 LegalCategory (3 categorías)
1. **Derecho Penal** ⚖️
2. **Derecho de Familia** 👨‍👩‍👧
3. **Derecho Civil** 📋

### 7.3 LegalService (10 servicios principales)

**Derecho Penal:**
1. Defensa en Ley 20.000 (Tráfico y microtráfico de drogas)
2. Defensa en VIF (Violencia Intrafamiliar)
3. Delitos contra las personas (homicidio, lesiones)
4. Beneficios penitenciarios (libertad condicional, reclusión parcial)
5. Apelaciones penales

**Derecho de Familia:**
6. Mediación familiar (custodia, alimentos)
7. Casos de VIF con peritaje psicosocial
8. Demandas de alimentos

**Derecho Civil:**
9. Cobranza judicial
10. Compraventa de inmuebles y escrituras

### 7.4 CaseType (ejemplos específicos)

**Ley 20.000:**
- Microtráfico Art. 3° (hasta 10g)
- Tráfico simple (más de 10g)
- Tráfico agravado

**VIF:**
- VIF con lesiones leves
- VIF con lesiones graves
- VIF psicológica

**Familia:**
- Custodia compartida
- Pensión alimenticia
- Regulación de visitas

### 7.5 FeeStructure (estructura de honorarios)

```python
# Ejemplo para Ley 20.000
service: "Defensa Ley 20.000"
structure_type: "mixed"  # parte fija + éxito
base_amount: 500000  # $500.000 inicial
success_fee: "negociable según resultado"
payment_plans_available: True
typical_payment_plan: "60% inicial, 40% al cierre"
notes: "Evaluación gratuita del caso. Facilidades de pago disponibles."
```

---

## 8. CAMBIOS EN SERVICIOS (app/services/)

### 8.1 Eliminar
- ❌ `products.py` (completo)
- ❌ `orders.py` (completo)
- ❌ `cart.py` (completo)

### 8.2 Renombrar/Adaptar
- ✅ `bookings.py` → mantener pero adaptar para consultas legales
- ✅ `quotes.py` → mantener para presupuestos

### 8.3 Crear NUEVOS
```python
# app/services/legal_services.py
async def search_legal_services(legal_area: str) -> List[dict]
async def get_service_info(service_id: str) -> dict

# app/services/case_inquiries.py
async def create_case_inquiry(...) -> dict
async def get_inquiry_status(...) -> dict

# app/services/fee_info.py
async def get_fee_structure(service_type: str) -> dict
async def get_payment_options() -> dict
```

---

## 9. CONSIDERACIONES IMPORTANTES

### 9.1 Aspectos Legales y Éticos ⚠️
1. **NUNCA dar asesoría legal definitiva** por chat
2. Siempre incluir disclaimer: "Esta es información general, no constituye asesoría legal"
3. Casos urgentes (detenido, audiencia próxima) → derivar INMEDIATAMENTE a abogado
4. No almacenar información sensible del caso en texto plano
5. Cumplir con GDPR/protección de datos personales

### 9.2 Privacidad
- Mensajes sensibles (confesión de delitos, detalles comprometedores)
- Encriptar campos sensibles en DB
- No compartir información de casos entre clientes

### 9.3 Urgencias
- Detector de palabras clave urgentes: "detenido", "audiencia mañana", "policía"
- Auto-escalación a HUMAN_SUPPORT con prioridad alta
- Notificación inmediata al abogado por WhatsApp

---

## 10. ESTIMACIÓN DE CAMBIOS

### Archivos a MODIFICAR (sustancial):
1. ✏️ `app/db/models.py` — eliminar Product/Order, agregar LegalService/CaseInquiry
2. ✏️ `app/intents/definitions.py` — eliminar 8 intents, agregar 7 nuevos
3. ✏️ `app/prompts/templates.py` — reescribir prompts para contexto legal
4. ✏️ `app/routers/webhook.py` — adaptar lógica de router de intents
5. ✏️ `seed_demo.py` — completamente nuevo para RJZ

### Archivos a ELIMINAR:
6. ❌ `app/services/products.py`
7. ❌ `app/services/orders.py`
8. ❌ `app/services/cart.py`

### Archivos a CREAR:
9. 🆕 `app/services/legal_services.py`
10. 🆕 `app/services/case_inquiries.py`
11. 🆕 `app/services/fee_info.py`
12. 🆕 `seed_legal_rzj.py` ← **ESTE ES EL QUE GENERAREMOS AHORA**

### Archivos a MANTENER (sin cambios o cambios menores):
- ✅ `app/ai/*` — clasificador y response builder (solo cambiar prompts)
- ✅ `app/whatsapp/*` — gateway y media (sin cambios)
- ✅ `app/services/bookings.py` — adaptar levemente
- ✅ `app/services/quotes.py` — mantener casi igual
- ✅ `app/services/leads.py` — sin cambios
- ✅ `app/services/notifications.py` — sin cambios
- ✅ `app/services/handoff.py` — sin cambios

---

## 11. ROADMAP DE IMPLEMENTACIÓN

### FASE 1 — Estructura Base (Día 1)
1. ✅ Analizar sistema actual
2. ✅ Diseñar nuevo modelo de datos
3. ✅ Generar seed para RJZ
4. Modificar `models.py` (eliminar Product/Order, agregar Legal*)
5. Modificar `definitions.py` (nuevos intents)

### FASE 2 — Lógica de Negocio (Día 2)
6. Crear `legal_services.py`
7. Crear `case_inquiries.py`
8. Crear `fee_info.py`
9. Adaptar `bookings.py`
10. Modificar router de intents en `webhook.py`

### FASE 3 — Prompts y Respuestas (Día 3)
11. Reescribir prompts en `templates.py`
12. Ajustar tono y estilo de respuestas
13. Agregar disclaimers legales
14. Testing con casos reales

### FASE 4 — Testing y Ajustes
15. Probar con preguntas frecuentes de RJZ
16. Ajustar sensibilidad de urgencias
17. Validar notificaciones a abogado
18. Optimizar tiempos de respuesta

---

## 12. MÉTRICAS DE ÉXITO

- ✅ **80%+ de consultas iniciales** clasificadas correctamente
- ✅ **100% de casos urgentes** escalados a humano en <1 min
- ✅ **Reducción 60%** en preguntas repetitivas al abogado
- ✅ **Aumento 40%** en leads convertidos a consultas
- ✅ **Tiempo promedio de respuesta** <30 segundos

---

## 13. PRÓXIMO PASO

**GENERAR `seed_legal_rzj.py`** con:
- Business "Mediaciones RJZ"
- 3 LegalCategory
- 10 LegalService con info real
- 15 CaseType basados en los delitos más consultados
- 5 FeeStructure estándar
- BusinessSettings con horarios, dirección, contacto

---

*Análisis preparado para migración de sistema restaurante → estudio jurídico*
*Fecha: 2024 | Sistema: WhatsApp AI Automation Engine*
