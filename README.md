# WhatsApp AI Automation Engine 🤖

Motor de automatización **WhatsApp + IA + Base de Datos** para PyMEs.  
Responde automáticamente usando **información real del negocio** — precios, productos, horarios, reservas y pedidos.

## Arquitectura del pipeline

```
WhatsApp (Meta Cloud API)
        │
        ▼
  [1] Intent Engine          ← OpenAI extrae intención + entidades
        │
        ▼
  [2] Action Router          ← Python ejecuta lógica con datos REALES de la DB
        │
        ▼
  [3] Response Builder       ← OpenAI formatea respuesta natural
        │
        ▼
WhatsApp → Cliente
```

### Intenciones detectadas

| Intent | Ejemplo |
|---|---|
| `PRICE_QUERY` | "¿Cuánto vale el completo italiano?" |
| `PRODUCT_INFO` | "¿Qué hamburguesas tienen?" |
| `ORDER_CREATE` | "Quiero pedir 2 completos dinámicos" |
| `ORDER_STATUS` | "¿Cómo va mi pedido?" |
| `BOOKING` | "Reservar mesa para mañana 8pm" |
| `HOURS_QUERY` | "¿A qué hora abren?" |
| `LOCATION_QUERY` | "¿Dónde están ubicados?" |
| `HUMAN_SUPPORT` | "Quiero hablar con alguien" |
| `GREETING` | "Hola buenos días" |

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | **FastAPI** (async) |
| Base de datos | **PostgreSQL** + SQLAlchemy async |
| IA | **OpenAI** gpt-4o-mini (structured outputs) |
| WhatsApp | **Meta Cloud API** |
| Containerización | **Docker** + docker-compose |

## Instalación rápida (desarrollo)

### 1. Clonar y configurar entorno

```bash
git clone <repo>
cd 24challenge
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 2. Variables de entorno

```bash
cp .env.example .env
# Editar .env con tus claves reales:
# - OPENAI_API_KEY
# - WHATSAPP_TOKEN
# - WHATSAPP_PHONE_NUMBER_ID
# - WHATSAPP_VERIFY_TOKEN
# - ADMIN_API_KEY
```

### 3. Levantar PostgreSQL

```bash
docker-compose up db -d
```

### 4. Iniciar servidor

```bash
uvicorn app.main:app --reload
```

Las tablas se crean automáticamente al iniciar.

### 5. Cargar datos demo (restaurante de ejemplo)

```bash
python seed_demo.py
```

### 6. Probar el pipeline SIN WhatsApp

```bash
python test_pipeline.py
```

## Instalación completa con Docker

```bash
cp .env.example .env
# Editar .env

docker-compose up --build
```

API disponible en `http://localhost:8000`  
Docs interactivos en `http://localhost:8000/docs`

## Configurar el webhook en Meta

1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. App → WhatsApp → Configuración → Webhooks
3. URL del webhook: `https://tudominio.com/webhook/{PHONE_NUMBER_ID}`
4. Token de verificación: el valor de `WHATSAPP_VERIFY_TOKEN` en tu `.env`
5. Suscríbete a: `messages`

> **Tip**: Para desarrollo local usa [ngrok](https://ngrok.com):  
> `ngrok http 8000`  
> La URL pública que da ngrok va como webhook en Meta.

## API de administración

Todos los endpoints del panel admin requieren el header:
```
X-Admin-Key: <tu ADMIN_API_KEY>
```

### Endpoints principales

```
POST   /admin/businesses                           Crear negocio
GET    /admin/businesses                           Listar negocios
PATCH  /admin/businesses/{id}                      Actualizar negocio

POST   /admin/businesses/{id}/categories           Crear categoría
POST   /admin/businesses/{id}/products             Crear producto
PATCH  /admin/businesses/{id}/products/{pid}       Actualizar producto
DELETE /admin/businesses/{id}/products/{pid}       Eliminar producto

GET    /admin/businesses/{id}/orders               Ver pedidos
PATCH  /admin/businesses/{id}/orders/{oid}/status  Actualizar estado pedido

GET    /admin/businesses/{id}/bookings             Ver reservas
PATCH  /admin/businesses/{id}/bookings/{bid}/status Confirmar/cancelar reserva

GET    /admin/businesses/{id}/leads                Ver leads
GET    /admin/businesses/{id}/conversations        Ver conversaciones
GET    /admin/businesses/{id}/dashboard            Dashboard resumen
```

### Ejemplo: registrar un negocio

```bash
curl -X POST http://localhost:8000/admin/businesses \
  -H "X-Admin-Key: tu_admin_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Restaurante",
    "phone_number_id": "1234567890",
    "whatsapp_token": "EAAxxxx...",
    "business_type": "restaurant",
    "welcome_message": "¡Hola! ¿En qué te ayudo?",
    "human_support_phone": "+56912345678",
    "address": "Av. Principal 123",
    "city": "Santiago",
    "hours": {
      "lunes": "09:00-22:00",
      "martes": "09:00-22:00",
      "sábado": "10:00-23:00"
    }
  }'
```

## Multi-tenant

El sistema soporta **múltiples negocios** en una sola instancia.  
Cada negocio tiene su propio `phone_number_id` de Meta y sus propios productos, pedidos y conversaciones.

## Nichos ideales para vender

- 🍔 **Restaurantes y fuentes de soda** — menú, precios, pedidos
- ☕ **Cafeterías** — carta, horarios, reservas de mesa  
- 🔧 **Talleres mecánicos** — cotizaciones, agendamiento de servicios
- 🏥 **Clínicas y centros médicos** — agendar horas, precios de consultas
- 🏪 **Tiendas y botillerías** — stock, precios, pedidos
- 🏗️ **Constructoras y ferreterías** — cotizaciones, disponibilidad

## Estructura del proyecto

```
app/
├── main.py              # FastAPI app + lifespan
├── config.py            # Variables de entorno (pydantic-settings)
├── ai/
│   ├── intent_classifier.py   # OpenAI → ExtractedIntent (structured output)
│   └── response_builder.py    # OpenAI → texto natural con datos reales
├── db/
│   ├── database.py      # Motor async SQLAlchemy
│   └── models.py        # ORM: Business, Product, Order, Booking, Lead, ...
├── intents/
│   └── definitions.py   # Enum Intent + Pydantic ExtractedIntent
├── prompts/
│   └── templates.py     # System prompts para clasificador y builder
├── routers/
│   ├── webhook.py       # POST /webhook/{phone_number_id} — pipeline principal
│   └── admin.py         # Panel de administración con API Key
├── services/
│   ├── products.py      # Búsqueda de productos en DB real
│   ├── orders.py        # Crear y consultar pedidos
│   ├── bookings.py      # Registrar reservas
│   ├── leads.py         # Captura de leads
│   └── handoff.py       # Derivar a humano
├── whatsapp/
│   └── gateway.py       # Meta Cloud API — envío de mensajes
└── models/
    └── schemas.py       # Schemas Pydantic para la API admin
```

## Licencia

MIT
# wsp-engiener-intents-response-ia
