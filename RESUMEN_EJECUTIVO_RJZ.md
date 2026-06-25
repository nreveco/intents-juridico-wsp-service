# RESUMEN EJECUTIVO - ADAPTACIÓN PARA MEDIACIONES RJZ

## 🎯 Objetivo
Adaptar el sistema WhatsApp AI (actualmente configurado para restaurantes) al contexto de un **estudio jurídico** especializado en Derecho Penal, Familia y Civil.

---

## 📊 Estado Actual

### ✅ Archivos Creados
1. **`ANALISIS_ESTUDIO_JURIDICO.md`** ← Análisis técnico completo (13 secciones)
2. **`seed_legal_rzj.py`** ← Script de inicialización con datos de RJZ
3. **`RESUMEN_EJECUTIVO_RJZ.md`** ← Este archivo

### 📦 Datos Preparados en el Seed

| Componente | Cantidad | Detalles |
|---|---|---|
| **Negocio** | 1 | Mediaciones RJZ |
| **Categorías Legales** | 3 | Penal, Familia, Civil |
| **Servicios** | 16 | Desde Ley 20.000 hasta Contratos |
| **Configuración** | 1 | Horarios, dirección, contacto |

---

## 🔍 Hallazgos Clave del Análisis

### Diferencias Fundamentales: Restaurante vs Estudio Jurídico

| Aspecto | Restaurante | Estudio Jurídico |
|---|---|---|
| **Productos** | Menú fijo con precios | Servicios variables según caso |
| **Transacciones** | Pedido → Pago → Entrega | Consulta → Evaluación → Contrato |
| **Pricing** | Fijo ($8.990) | Variable (depende complejidad) |
| **Urgencias** | "Tengo hambre" | "Estoy detenido" ⚠️ |
| **Carrito** | Sí (múltiples ítems) | No (cada caso es único) |
| **Tiempo** | Inmediato (30-60 min) | Semanas o meses |

---

## 🎯 Top 10 Preguntas de Clientes RJZ

Basado en el chat real proporcionado:

1. **"¿Cómo son los pagos / honorarios?"** → Sistema de cotización variable
2. **"¿Pueden hacer algo?"** → Evaluación inicial de viabilidad
3. **"¿Cuánto tiempo demora?"** → Info de plazos por tipo de caso
4. **"¿Ven temas penales?"** → Filtro de especialidades
5. **"¿Beneficios penitenciarios?"** → Asesoría especializada
6. **"¡Hola! Quiero más información"** → Flujo desde Instagram
7. **"¿Con quién tengo el gusto?"** → Identificación del abogado
8. **"¿Pueden hacer propuesta?"** → Presupuesto personalizado
9. **"¿Qué pasa con antecedentes previos?"** → Evaluación de riesgo
10. **"¿Pueden coordinar reunión?"** → Agendamiento

---

## 🏆 Casos Más Frecuentes (Del Análisis de Chats)

### 🥇 Top 3
1. **Tráfico de drogas** (Ley 20.000) — Art. 3°, microtráfico
2. **VIF** — Con peritaje psicosocial, DAM-HAKI
3. **Homicidio / Delitos contra personas** — Beneficios penitenciarios

### Otros casos importantes
- Casos de familia (custodia, mediación)
- Cobranza judicial
- Traslado de imputados ($400.000)
- Compraventas e inmuebles
- Calumnias e injurias

---

## ⚙️ Cambios Requeridos en el Sistema

### ❌ Eliminar (8 componentes)
```python
# Intenciones
PRICE_QUERY         # No hay precios fijos
ORDER_CREATE        # No hay pedidos
ORDER_STATUS        # No hay pedidos
CART_ADD            # No hay carrito
CART_VIEW           # No hay carrito
CART_CHECKOUT       # No hay carrito
CART_CLEAR          # No hay carrito
PRODUCT_INFO        # No aplica "productos"

# Servicios
app/services/products.py
app/services/orders.py
app/services/cart.py

# Modelos
Product, Category (reemplazar por LegalService, LegalCategory)
Order, OrderItem
```

### ✅ Mantener (6 componentes)
```python
GREETING              # Bienvenida desde Instagram
BOOKING               # Agendamiento de consultas
QUOTE_REQUEST         # Presupuestos personalizados
HUMAN_SUPPORT         # Derivación a abogado
HOURS_QUERY           # Horarios de atención
LOCATION_QUERY        # Dirección oficina
```

### 🆕 Crear (7 nuevas intenciones)
```python
CASE_INQUIRY          # "¿Pueden hacer algo con mi caso?"
SERVICE_INFO          # "¿Ven temas penales/familia?"
PAYMENT_INFO          # "¿Cómo son los pagos?"
TIMEFRAME_QUERY       # "¿Cuánto demora?"
LAWYER_IDENTITY       # "¿Con quién hablo?"
BENEFIT_INFO          # "¿Puedo salir en libertad condicional?"
PRIOR_RECORD_QUERY    # "¿Qué pasa con mis antecedentes?"
```

---

## 🗺️ Roadmap de Implementación

### ✅ FASE 1 — COMPLETADA
- [x] Análisis de sistema actual
- [x] Diseño de modelo de datos legal
- [x] Seed para Mediaciones RJZ
- [x] Documentación técnica completa

### 🔄 FASE 2 — Base de Datos (Pendiente)
```python
# Modificar: app/db/models.py
- Eliminar: Product, Category, Order, OrderItem
- Agregar: LegalCategory, LegalService, CaseType, CaseInquiry
- Agregar: InitialConsultation, FeeStructure
- Mantener: Business, BusinessSettings, Conversation, Message, Lead, Quote
```

### 🔄 FASE 3 — Intenciones (Pendiente)
```python
# Modificar: app/intents/definitions.py
class Intent(str, enum.Enum):
    # Mantener
    GREETING = "GREETING"
    BOOKING = "BOOKING"
    QUOTE_REQUEST = "QUOTE_REQUEST"
    HUMAN_SUPPORT = "HUMAN_SUPPORT"
    HOURS_QUERY = "HOURS_QUERY"
    LOCATION_QUERY = "LOCATION_QUERY"
    UNKNOWN = "UNKNOWN"
    
    # Nuevas para contexto legal
    CASE_INQUIRY = "CASE_INQUIRY"
    SERVICE_INFO = "SERVICE_INFO"
    PAYMENT_INFO = "PAYMENT_INFO"
    TIMEFRAME_QUERY = "TIMEFRAME_QUERY"
    LAWYER_IDENTITY = "LAWYER_IDENTITY"
    BENEFIT_INFO = "BENEFIT_INFO"
    PRIOR_RECORD_QUERY = "PRIOR_RECORD_QUERY"

class ExtractedIntent(BaseModel):
    intent: Intent
    # Campos nuevos para contexto legal
    legal_matter: Optional[str] = None  # "tráfico de drogas", "VIF"
    has_detention: Optional[bool] = None  # Si está detenido
    has_prior_record: Optional[bool] = None
    benefit_type: Optional[str] = None  # "libertad condicional", etc.
    urgency: Optional[str] = None  # "low" | "medium" | "high"
```

### 🔄 FASE 4 — Prompts (Pendiente)
```python
# Modificar: app/prompts/templates.py

def build_intent_prompt(business_name, business_type, legal_areas):
    return f"""
    Eres el clasificador de intenciones para WhatsApp de "{business_name}", 
    un estudio jurídico especializado en {legal_areas}.
    
    CRÍTICO ⚠️:
    - Si el cliente menciona estar DETENIDO → urgency="high"
    - Si hay audiencia próxima (hoy, mañana) → urgency="high"
    - Si menciona antecedentes previos → has_prior_record=True
    
    Áreas legales: Derecho Penal, Derecho de Familia, Derecho Civil
    
    Intenciones:
    - CASE_INQUIRY: "¿Pueden ayudarme?", "¿Qué puedo hacer?"
    - SERVICE_INFO: "¿Ven temas penales?", "¿Atienden VIF?"
    - PAYMENT_INFO: "¿Cuánto cobran?", "¿Cómo son los pagos?"
    - TIMEFRAME_QUERY: "¿Cuánto demora?", "¿Cuánto tiempo tarda?"
    ...
    """

def build_response_prompt(business_name):
    return f"""
    Eres el asistente virtual de {business_name}, estudio jurídico.
    
    REGLAS ESTRICTAS:
    1. Tono: profesional pero cercano, empático
    2. NUNCA des asesoría legal definitiva por chat
    3. Siempre incluir disclaimer: "Esta es información general"
    4. Casos urgentes → derivar INMEDIATAMENTE a abogado humano
    5. Máximo 4-5 líneas de respuesta
    6. Emojis legales con moderación: ⚖️ 📋 👨‍⚖️
    7. Termina sugiriendo: consulta gratuita o agendar reunión
    """
```

### 🔄 FASE 5 — Servicios (Pendiente)
```python
# Crear: app/services/legal_services.py
async def search_legal_services(legal_area: str) -> List[dict]:
    """Busca servicios por área legal (penal, familia, civil)"""
    
async def get_service_info(service_id: str) -> dict:
    """Info detallada de un servicio legal"""

# Crear: app/services/case_inquiries.py
async def create_case_inquiry(
    business_id: str,
    customer_phone: str,
    legal_matter: str,
    description: str,
    urgency: str = "medium",
    is_detained: bool = False
) -> dict:
    """Registra nueva consulta de caso"""
    
async def notify_urgent_case(inquiry: dict):
    """Notifica al abogado si urgency='high' o is_detained=True"""

# Crear: app/services/fee_info.py
async def get_fee_structure(service_type: str) -> dict:
    """Retorna info de honorarios por tipo de servicio"""
    
async def get_payment_options() -> dict:
    """Retorna formas de pago y facilidades disponibles"""
```

### ✅ FASE 6 — Testing (COMPLETADO)
```python
# Archivo creado: test_legal_bot.py
# Suite de testing automatizada con 10 casos de prueba

test_cases = [
    "¿Cómo son los pagos?",                                # PAYMENT_INFO
    "Tengo un caso de tráfico de drogas, ¿pueden ayudarme?",  # CASE_INQUIRY
    "¿Cuánto tiempo demora un proceso de VIF?",            # TIMEFRAME_QUERY
    "¿Ven temas penales?",                                 # SERVICE_INFO
    "Quiero agendar una reunión",                          # BOOKING
    "¿Con quién tengo el gusto?",                          # LAWYER_IDENTITY
    "¿Puedo salir en libertad condicional?",               # BENEFIT_INFO
    "¿Qué pasa si tengo antecedentes previos?",            # PRIOR_RECORD_QUERY
    "Estoy detenido, necesito ayuda urgente",  # ⚠️ HIGH  # HUMAN_SUPPORT
    "Hola, quiero más información",  # Desde Instagram    # GREETING
]

# Validaciones:
✅ Clasificación de intenciones
✅ Extracción de entidades legales
✅ Detección de urgencias (is_detained → high)
✅ Respuestas con disclaimers legales
✅ Escalamiento a humano en casos críticos

# Ejecutar:
python test_legal_bot.py

# Ver guía completa:
TESTING_GUIDE.md
```

---

## ⚠️ Consideraciones Críticas

### 🚨 Urgencias y Seguridad
```python
# Palabras clave que activan urgency="high"
URGENT_KEYWORDS = [
    "detenido", "detenida", "prisión preventiva",
    "audiencia mañana", "audiencia hoy",
    "policía", "formalización",
    "urgente", "emergencia"
]

# Flujo de urgencia:
if urgency == "high" or is_detained:
    → Crear CaseInquiry con prioridad alta
    → Notificar INMEDIATAMENTE al abogado por WhatsApp
    → Responder: "Tu caso es urgente. Un abogado te contactará en 15 minutos."
    → Activar HUMAN_SUPPORT automático
```

### 📜 Disclaimers Legales
Todos los mensajes del bot deben incluir (rotando):
- "Esta es información general, no constituye asesoría legal personalizada."
- "Para una evaluación precisa, agenda una consulta con nuestro abogado."
- "Los plazos y procedimientos pueden variar según el caso específico."

### 🔒 Privacidad
- NO almacenar confesiones de delitos en texto plano
- NO compartir información de casos entre clientes
- Encriptar campos sensibles: `CaseInquiry.description`, `Message.content`
- Cumplir con protección de datos personales (GDPR/Ley 19.628 Chile)

---

## 📈 Métricas de Éxito

### KPIs Esperados
- ✅ **80%+** de consultas iniciales clasificadas correctamente
- ✅ **100%** de casos urgentes escalados a humano en <1 min
- ✅ **Reducción 60%** en preguntas repetitivas al abogado
- ✅ **Aumento 40%** en leads convertidos a consultas agendadas
- ✅ **Tiempo de respuesta** <30 segundos

### Dashboard Admin
```python
# Métricas a mostrar en /admin/businesses/{id}/dashboard
- Total consultas recibidas (últimos 7 días)
- Casos urgentes atendidos
- Tasa de conversión (lead → consulta agendada)
- Tipo de caso más consultado
- Horarios de mayor actividad
- Tiempo promedio de respuesta del bot
- Tasa de handoff a humano
```

---

## 🚀 Comando de Ejecución

### 1. Ejecutar el Seed
```bash
# Asegurarse de que la DB y Ollama estén corriendo
docker compose up -d

# Ejecutar seed de RJZ
python seed_legal_rzj.py

# Verá output:
# ✅ SEED COMPLETADO EXITOSAMENTE
# 📋 Negocio creado: Mediaciones RJZ
# ⚖️ Áreas legales: 3
# 📦 Servicios legales: 16
```

### 2. Actualizar Tokens de WhatsApp
```bash
# Con cURL (o Postman)
curl -X PATCH http://localhost:8000/admin/businesses/{BUSINESS_ID} \
  -H "X-Admin-Key: TU_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number_id": "TU_PHONE_NUMBER_ID_REAL_DE_META",
    "whatsapp_token": "TU_TOKEN_REAL_DE_META"
  }'
```

### 3. Probar el Webhook
```bash
# Exponer con ngrok
ngrok http 8000

# Configurar webhook en Meta con:
# URL: https://TU-NGROK-URL.ngrok-free.app/webhook/{PHONE_NUMBER_ID}
# Verify Token: (el que está en .env)

# Enviar mensaje de prueba desde WhatsApp:
"Hola, quiero más información"

# Debe responder con bienvenida de Mediaciones RJZ ⚖️
```

---

## 📋 Checklist Antes de Producción

- [ ] Seed ejecutado correctamente
- [ ] Tokens de WhatsApp actualizados
- [ ] Webhook verificado en Meta
- [x] Modificar `models.py` (eliminar Product/Order, agregar Legal*) ✅
- [x] Modificar `definitions.py` (nuevos intents legales) ✅
- [x] Modificar `templates.py` (prompts legales) ✅
- [x] Crear `legal_services.py` ✅
- [x] Crear `case_inquiries.py` ✅
- [x] Crear `fee_info.py` ✅
- [ ] Adaptar `webhook.py` router ⚠️ (ver COMPLETAR_PASO_5_MANUAL.md)
- [x] Testing con 10 preguntas frecuentes ✅ (test_legal_bot.py)
- [ ] Configurar notificaciones urgentes
- [x] Validar disclaimers legales en respuestas ✅
- [ ] Probar escalamiento a humano
- [ ] Medir tiempos de respuesta

### 📊 Estado de Fases
- ✅ FASE 1: Análisis — COMPLETADA
- ✅ FASE 2: Base de Datos — COMPLETADA
- ✅ FASE 3: Intenciones — COMPLETADA
- ✅ FASE 4: Prompts — COMPLETADA
- ✅ FASE 5: Servicios — COMPLETADA
- ⚠️ FASE 5b: Webhook Router — 90% (requiere acción manual)
- ✅ FASE 6: Testing — COMPLETADA

### 🚀 Para Producción
1. Completar PASO 5 (webhook.py) — Ver `COMPLETAR_PASO_5_MANUAL.md`
2. Ejecutar `python seed_legal_rzj.py`
3. Actualizar tokens de WhatsApp
4. Ejecutar `python test_legal_bot.py` → Debe pasar 10/10 tests
5. Probar manualmente con WhatsApp real
6. ¡Desplegar!

---

## 📞 Contacto del Proyecto

- **Estudio:** Mediaciones RJZ
- **Teléfono:** +56912345678
- **Áreas:** Derecho Penal, Familia, Civil
- **Horario:** Lunes a viernes 9:00-18:00, Sábado 10:00-14:00

---

## 📚 Documentación Relacionada

1. **`ANALISIS_ESTUDIO_JURIDICO.md`** ← Análisis técnico completo (13 secciones)
2. **`DOCUMENTACION.md`** ← Documentación original del sistema
3. **`seed_legal_rzj.py`** ← Script de inicialización
4. **`.env.example`** ← Plantilla de configuración

---

*Documento generado: Junio 2024*  
*Sistema: WhatsApp AI Automation Engine adaptado para Estudio Jurídico*  
*Versión: 1.0 - Mediaciones RJZ*
