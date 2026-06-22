# 📋 MEDIACIONES RJZ - DOCUMENTACIÓN DEL PROYECTO
## Sistema WhatsApp AI adaptado para Estudio Jurídico

---

## 🎯 Objetivo del Proyecto

Transformar el sistema WhatsApp AI Automation Engine (originalmente diseñado para restaurantes) en un asistente virtual especializado para el **Estudio Jurídico Mediaciones RJZ**, con capacidad de:

- ✅ Atender consultas legales 24/7
- ✅ Clasificar casos por área legal (Penal, Familia, Civil)
- ✅ Detectar urgencias automáticamente
- ✅ Agendar consultas
- ✅ Proveer información de honorarios
- ✅ Escalar casos críticos a abogado humano

---

## 📚 Documentación Generada

### 1. **ANALISIS_ESTUDIO_JURIDICO.md** (20 KB) ⭐
**El documento maestro técnico con 13 secciones:**

```
Contenido:
├── 1. Análisis del contexto actual
├── 2. Mapeo de funcionalidades (Mantener/Eliminar/Crear)
├── 3. Nuevo modelo de datos (7 tablas nuevas)
├── 4. Nuevas intenciones (7 intents legales)
├── 5. Flujos principales rediseñados
├── 6. Adaptaciones en prompts
├── 7. Seed data para RJZ
├── 8. Cambios en servicios
├── 9. Consideraciones legales y éticas ⚠️
├── 10. Estimación de cambios (12 archivos)
├── 11. Roadmap de implementación (4 fases)
├── 12. Métricas de éxito
└── 13. Próximos pasos
```

**Leer primero:** Este es el blueprint completo del proyecto.

---

### 2. **seed_legal_rzj.py** (16 KB) ⚙️
**Script de inicialización de base de datos**

```python
# Carga automática de:
✅ 1 Business (Mediaciones RJZ)
✅ 3 LegalCategory (Penal, Familia, Civil)
✅ 16 LegalService (desde Ley 20.000 hasta Contratos)
✅ 1 BusinessSettings (horarios, dirección)

# Ejecución:
python seed_legal_rzj.py
```

**Servicios incluidos:**
- Defensa Penal - Ley 20.000 (Drogas)
- Defensa en VIF
- Delitos contra las Personas
- Beneficios Penitenciarios
- Apelaciones Penales
- Calumnias e Injurias
- Mediación Familiar
- Custodia y Cuidado Personal
- Pensión de Alimentos
- Regulación de Visitas
- Cobranza Judicial
- Compraventa de Inmuebles
- Regularización de Propiedades
- Redacción de Contratos
- Consulta Legal Presencial
- Traslado de Imputados

---

### 3. **RESUMEN_EJECUTIVO_RJZ.md** (13 KB) 📊
**Vista de alto nivel para gerentes y stakeholders**

```
Contenido:
├── Estado actual del proyecto
├── Hallazgos clave del análisis
├── Top 10 preguntas de clientes RJZ (del chat real)
├── Casos más frecuentes (Ley 20.000, VIF, Homicidio)
├── Roadmap de implementación (6 fases)
├── Consideraciones críticas (urgencias, disclaimers)
├── Métricas de éxito (KPIs)
├── Checklist antes de producción
└── Comandos de ejecución
```

**Ideal para:** Presentaciones ejecutivas y planning.

---

### 4. **FLUJOS_CONVERSACIONALES_RJZ.md** (32 KB) 💬
**10 ejemplos completos de conversaciones reales**

```
Flujos documentados:
├── 1. Cliente desde Instagram (Lead Capture)
├── 2. "¿Ven temas penales?" (Service Info)
├── 3. "¿Pueden hacer algo?" (Case Inquiry - CRÍTICO)
├── 4. "¿Cuánto cobran?" (Payment Info)
├── 5. "¿Cuánto demora?" (Timeframe Query)
├── 6. "¿Con quién hablo?" (Lawyer Identity)
├── 7. Beneficios Penitenciarios
├── 8. URGENCIA MÁXIMA - Cliente Detenido 🚨
├── 9. Antecedentes Previos (Risk Assessment)
└── 10. Agendamiento de Consulta

+ Matriz de decisión: Cuándo escalar a humano
```

**Incluye:** Inputs del cliente, respuestas del bot, queries a DB, notificaciones.

---

## 🔍 Análisis de Preguntas Reales (Del Chat RJZ)

### Top 10 Preguntas Frecuentes
Extraídas del historial de WhatsApp real del estudio:

| # | Pregunta | Frecuencia | Intent Propuesto |
|---|---|---|---|
| 1 | ¿Cómo son los pagos/honorarios? | ⭐⭐⭐⭐⭐ | `PAYMENT_INFO` |
| 2 | ¿Pueden hacer algo? ¿Qué podemos hacer? | ⭐⭐⭐⭐⭐ | `CASE_INQUIRY` |
| 3 | ¿Cuánto tiempo demora? | ⭐⭐⭐⭐ | `TIMEFRAME_QUERY` |
| 4 | ¿Ven temas penales? | ⭐⭐⭐⭐ | `SERVICE_INFO` |
| 5 | ¿Beneficios penitenciarios? | ⭐⭐⭐ | `BENEFIT_INFO` |
| 6 | ¡Hola! Quiero más información | ⭐⭐⭐⭐⭐ | `GREETING` |
| 7 | ¿Con quién tengo el gusto? | ⭐⭐ | `LAWYER_IDENTITY` |
| 8 | ¿Pueden hacer propuesta? | ⭐⭐⭐ | `QUOTE_REQUEST` |
| 9 | ¿Qué pasa con antecedentes previos? | ⭐⭐⭐ | `PRIOR_RECORD_QUERY` |
| 10 | ¿Pueden coordinar reunión? | ⭐⭐⭐⭐ | `BOOKING` |

### Casos Más Frecuentes

| Ranking | Delito/Materia | Volumen | Observaciones |
|---|---|---|---|
| 🥇 | **Tráfico de drogas** (Ley 20.000) | ⭐⭐⭐⭐⭐ | Art. 3° (microtráfico), antecedentes previos |
| 🥈 | **VIF** | ⭐⭐⭐⭐ | Con peritaje psicosocial, DAM-HAKI |
| 🥉 | **Homicidio / Delitos contra personas** | ⭐⭐⭐ | Beneficios penitenciarios frecuentes |
| 4 | Familia (custodia, mediación) | ⭐⭐⭐ | Casos Tatiana, Jairo |
| 5 | Cobranza judicial | ⭐⭐ | Incluye cobranza de condominios |
| 6 | Traslado de imputados | ⭐⭐ | $400.000 con facilidades |
| 7 | Compraventas e inmuebles | ⭐⭐ | Escrituras, regularización |
| 8 | Calumnias e injurias | ⭐ | Post-VIF generalmente |

---

## 🚀 Quick Start

### Paso 1: Revisar la Documentación
```bash
# Leer en este orden:
1. README_RJZ.md (este archivo) ← Estás aquí
2. RESUMEN_EJECUTIVO_RJZ.md (contexto general)
3. ANALISIS_ESTUDIO_JURIDICO.md (diseño técnico)
4. FLUJOS_CONVERSACIONALES_RJZ.md (ejemplos)
```

### Paso 2: Ejecutar el Seed
```bash
# Asegurarse de que Docker está corriendo
docker compose up -d

# Esperar a que Ollama descargue el modelo (primera vez)
docker compose logs -f ollama-init

# Ejecutar seed para RJZ
python seed_legal_rzj.py

# Output esperado:
# ✅ SEED COMPLETADO EXITOSAMENTE
# 📋 Negocio creado: Mediaciones RJZ
# ⚖️ Áreas legales: 3
# 📦 Servicios legales: 16
```

### Paso 3: Actualizar Tokens de WhatsApp
```bash
# Obtener de Meta Developers:
# - PHONE_NUMBER_ID
# - WHATSAPP_TOKEN

# Actualizar vía API:
curl -X PATCH http://localhost:8000/admin/businesses/{BUSINESS_ID} \
  -H "X-Admin-Key: TU_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number_id": "123456789012345",
    "whatsapp_token": "EAAxxxxxxxx..."
  }'
```

### Paso 4: Probar
```bash
# Terminal 1: ngrok
ngrok http 8000

# Terminal 2: Ver logs
docker compose logs -f app

# Configurar webhook en Meta con URL ngrok
# Enviar desde WhatsApp: "Hola"
# Debe responder: "¡Hola! Bienvenido a Mediaciones RJZ ⚖️"
```

---

## ⚙️ Cambios Pendientes en el Código

### ❌ Eliminar (8 archivos/componentes)
```python
# Intenciones obsoletas
PRICE_QUERY, ORDER_CREATE, ORDER_STATUS
CART_ADD, CART_VIEW, CART_CHECKOUT, CART_CLEAR
PRODUCT_INFO

# Servicios obsoletos
app/services/products.py
app/services/orders.py
app/services/cart.py

# Modelos obsoletos
Product, Category → Reemplazar por LegalService, LegalCategory
Order, OrderItem → Eliminar completamente
```

### 🆕 Crear (7 componentes nuevos)
```python
# Nuevas intenciones (app/intents/definitions.py)
CASE_INQUIRY          # "¿Pueden ayudarme con mi caso?"
SERVICE_INFO          # "¿Ven temas penales?"
PAYMENT_INFO          # "¿Cómo son los pagos?"
TIMEFRAME_QUERY       # "¿Cuánto demora?"
LAWYER_IDENTITY       # "¿Con quién hablo?"
BENEFIT_INFO          # "¿Beneficios penitenciarios?"
PRIOR_RECORD_QUERY    # "¿Qué pasa con mis antecedentes?"

# Nuevos servicios
app/services/legal_services.py     # Búsqueda de servicios legales
app/services/case_inquiries.py     # Gestión de consultas de casos
app/services/fee_info.py            # Info de honorarios

# Nuevos modelos (app/db/models.py)
LegalCategory        # Reemplaza Category
LegalService         # Reemplaza Product
CaseType             # Tipos de casos con info estructurada
CaseInquiry          # Consulta inicial del cliente
InitialConsultation  # Renombrar Booking
FeeStructure         # Estructura de honorarios
```

---

## 🔥 Casos de Uso Críticos

### 🚨 Urgencia Máxima: Cliente Detenido
```python
# Detección automática:
keywords = ["detenido", "prisión preventiva", "audiencia mañana"]

# Acción inmediata:
if any(keyword in message.lower() for keyword in keywords):
    urgency = "CRITICAL"
    notify_lawyer_immediately()  # WhatsApp + SMS + Email
    response = "🚨 Tu caso es urgente. Un abogado te contactará en 15 minutos."
    conversation.status = "HUMAN_HANDOFF"
```

### ⚖️ Evaluación de Caso Complejo
```python
# Ejemplo: Cliente con antecedentes + nueva detención
if case.has_prior_record and case.new_arrest:
    complexity = "HIGH"
    requires_lawyer_eval = True
    response = """
    ⚠️ Tu caso requiere evaluación urgente.
    Los antecedentes previos pueden agravar tu situación.
    Primera consulta GRATIS - no esperes más.
    """
```

---

## 📊 Métricas de Éxito Esperadas

| Métrica | Objetivo | Medición |
|---|---|---|
| Clasificación correcta de intents | 80%+ | Test con 50 msgs reales |
| Escalamiento de urgencias | <1 min | Timer desde detección |
| Leads convertidos a consultas | +40% | Antes/después |
| Reducción preguntas repetitivas | 60% | Volumen msg al abogado |
| Tiempo respuesta bot | <30 seg | Promedio mensajes |
| Satisfacción del cliente | 4.5/5 | Survey post-consulta |

---

## ⚠️ Disclaimers Legales (CRÍTICO)

**Todos los mensajes del bot deben rotar estos disclaimers:**

```
1. "Esta es información general. No constituye asesoría legal personalizada."

2. "Para una evaluación precisa de tu caso, agenda una consulta con nuestro abogado."

3. "Los plazos y procedimientos pueden variar según el caso específico."

4. "Primera consulta GRATUITA. Evaluamos tu caso sin compromiso."
```

**Nunca:**
- ❌ Dar consejos legales definitivos
- ❌ Garantizar resultados ("ganarás el caso")
- ❌ Comprometer plazos exactos sin evaluar
- ❌ Almacenar confesiones de delitos en texto plano

---

## 📞 Información del Estudio

```
Nombre:    Mediaciones RJZ
Dirección: Av. Libertador Bernardo O'Higgins 1234, Oficina 501
           Santiago, Chile
Teléfono:  +56912345678
Horario:   Lun-Vie 9:00-18:00 | Sáb 10:00-14:00

Áreas:
  ⚖️  Derecho Penal
  👨‍👩‍👧 Derecho de Familia
  📋 Derecho Civil

WhatsApp:  +56912345678 (número a configurar en Meta)
```

---

## 🗂️ Estructura de Archivos del Proyecto

```
wsp-engiener-intents-response-ia/
│
├── 📄 Documentación RJZ (NUEVOS)
│   ├── README_RJZ.md                      ← Este archivo (índice)
│   ├── ANALISIS_ESTUDIO_JURIDICO.md       ← Diseño técnico completo
│   ├── RESUMEN_EJECUTIVO_RJZ.md           ← Vista ejecutiva
│   └── FLUJOS_CONVERSACIONALES_RJZ.md     ← Ejemplos de conversaciones
│
├── 🐍 Scripts de Inicialización
│   ├── seed_legal_rzj.py                  ← Seed para RJZ (NUEVO)
│   └── seed_demo.py                       ← Seed original (restaurante)
│
├── 📄 Documentación Original
│   ├── DOCUMENTACION.md                   ← Doc técnica original
│   └── README.md                          ← README original
│
├── 🐳 Docker
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── .env.example
│
├── 📦 Aplicación
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── db/
│       │   ├── models.py                  ← [MODIFICAR] Agregar Legal*
│       │   └── database.py
│       ├── intents/
│       │   └── definitions.py             ← [MODIFICAR] Nuevos intents
│       ├── prompts/
│       │   └── templates.py               ← [MODIFICAR] Prompts legales
│       ├── services/
│       │   ├── legal_services.py          ← [CREAR]
│       │   ├── case_inquiries.py          ← [CREAR]
│       │   ├── fee_info.py                ← [CREAR]
│       │   ├── products.py                ← [ELIMINAR]
│       │   ├── orders.py                  ← [ELIMINAR]
│       │   └── cart.py                    ← [ELIMINAR]
│       ├── ai/
│       │   ├── intent_classifier.py
│       │   ├── response_builder.py
│       │   └── media_processor.py
│       ├── whatsapp/
│       │   ├── gateway.py
│       │   ├── interactive.py
│       │   └── media.py
│       └── routers/
│           ├── webhook.py                 ← [MODIFICAR] Router de intents
│           └── admin.py
│
└── 🧪 Tests
    └── test_pipeline.py
```

---

## 🎯 Roadmap Resumido

### ✅ Fase 1: COMPLETADA
- [x] Análisis del sistema actual
- [x] Diseño del modelo de datos legal
- [x] Seed para Mediaciones RJZ
- [x] Documentación completa (4 archivos)

### 🔄 Fase 2: Modelos (Pendiente)
- [ ] Modificar `app/db/models.py`
- [ ] Agregar: LegalCategory, LegalService, CaseType, CaseInquiry, FeeStructure
- [ ] Eliminar: Product, Category, Order, OrderItem

### 🔄 Fase 3: Intenciones (Pendiente)
- [ ] Modificar `app/intents/definitions.py`
- [ ] Agregar 7 intents legales
- [ ] Eliminar 8 intents de restaurante

### 🔄 Fase 4: Servicios (Pendiente)
- [ ] Crear `app/services/legal_services.py`
- [ ] Crear `app/services/case_inquiries.py`
- [ ] Crear `app/services/fee_info.py`
- [ ] Eliminar products.py, orders.py, cart.py

### 🔄 Fase 5: Prompts (Pendiente)
- [ ] Modificar `app/prompts/templates.py`
- [ ] Adaptar tono legal
- [ ] Agregar disclaimers

### 🔄 Fase 6: Testing (Pendiente)
- [ ] Probar con 10 preguntas frecuentes
- [ ] Validar escalamiento de urgencias
- [ ] Medir métricas de éxito

---

## 💡 Tips para el Desarrollador

### Priorizar Urgencias
```python
# Siempre detectar primero palabras críticas
CRITICAL_KEYWORDS = [
    "detenido", "detenida", "preso", "presa",
    "audiencia hoy", "audiencia mañana",
    "prisión preventiva", "formalización",
    "urgente", "emergencia"
]
```

### Disclaimers Rotativos
```python
DISCLAIMERS = [
    "Esta es información general, no constituye asesoría legal.",
    "Para una evaluación precisa, agenda consulta con nuestro abogado.",
    "Los plazos pueden variar según el caso específico.",
]
# Rotar aleatoriamente en cada respuesta
```

### Logging de Casos Sensibles
```python
# NO guardar confesiones de delitos en logs
if message_contains_confession(message):
    log.info(f"Case inquiry from {phone} - DETAILS OMITTED FOR PRIVACY")
    # NO: log.info(f"Client said: {message}")
```

---

## 📖 Lecturas Recomendadas

1. **Primero:** `RESUMEN_EJECUTIVO_RJZ.md` (contexto general)
2. **Segundo:** `FLUJOS_CONVERSACIONALES_RJZ.md` (ver ejemplos)
3. **Tercero:** `ANALISIS_ESTUDIO_JURIDICO.md` (diseño técnico)
4. **Cuarto:** `DOCUMENTACION.md` (doc original del sistema)

---

## 🆘 Soporte

**Preguntas técnicas:**
- Revisar `ANALISIS_ESTUDIO_JURIDICO.md` sección 16 (Solución de problemas)
- Logs: `docker compose logs -f app`

**Preguntas de negocio:**
- Revisar `RESUMEN_EJECUTIVO_RJZ.md`
- Contactar al estudio: +56912345678

---

## 📜 Licencia y Uso

Este proyecto es una adaptación del WhatsApp AI Automation Engine para uso exclusivo de **Mediaciones RJZ**.

**Incluye:**
- ✅ Ollama (LLM local) - MIT License
- ✅ FastAPI - MIT License
- ✅ faster-whisper - MIT License
- ✅ Meta Cloud API - Terms of Service

**Costo de IA:** $0.00 (todo local)

---

*Documentación generada: Junio 2024*  
*Proyecto: WhatsApp AI para Mediaciones RJZ*  
*Versión: 1.0*  
*Estado: Ready for Implementation ✅*
