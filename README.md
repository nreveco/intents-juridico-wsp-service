# WhatsApp AI Automation Engine 🤖

Motor de automatización **WhatsApp + IA local + Base de Datos** para PyMEs.  
Responde automáticamente usando **información real del negocio** — precios, productos, horarios, reservas y pedidos.  
**Sin costos de API de IA** — corre completamente en local con [Ollama](https://ollama.com).

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | **FastAPI** (async) |
| Base de datos | **PostgreSQL 16** + SQLAlchemy async |
| LLM local | **Ollama** — `qwen2.5:7b` / `llama3.2:3b` |
| Transcripción de voz | **faster-whisper** (CPU, sin API externa) |
| Visión | **Ollama Vision** — `llava:7b` |
| WhatsApp | **Meta Cloud API** |
| Containerización | **Docker Compose** (app + db + ollama) |

## Pipeline de un mensaje

```
WhatsApp (Meta Cloud API)
        │
        ▼
  [1] Media Processor        ← faster-whisper (audio) / Ollama Vision (imagen) / pypdf (PDF)
        │
        ▼
  [2] Intent Classifier      ← Ollama: extrae intención + entidades (JSON mode + Pydantic)
        │
        ▼
  [3] Action Router          ← Python ejecuta lógica con datos REALES de la DB
        │
        ▼
  [4] Response Builder       ← Ollama: formatea respuesta natural en español
        │
        ▼
WhatsApp → Cliente
```

## Intenciones detectadas (15)

| Intent | Ejemplo |
|---|---|
| `PRICE_QUERY` | "¿Cuánto vale el completo italiano?" |
| `PRODUCT_INFO` | "¿Qué hamburguesas tienen?" |
| `ORDER_CREATE` | "Quiero pedir 2 completos dinámicos" |
| `ORDER_STATUS` | "¿Cómo va mi pedido?" |
| `BOOKING` | "Reservar mesa para mañana 8pm" |
| `QUOTE_REQUEST` | "Necesito cotización para pintar mi auto" |
| `CART_ADD` | "Agrega una Coca-Cola" |
| `CART_VIEW` | "¿Qué tengo en el carrito?" |
| `CART_CHECKOUT` | "Confirmar pedido, listo" |
| `CART_CLEAR` | "Cancelar, empezar de nuevo" |
| `HOURS_QUERY` | "¿A qué hora abren?" |
| `LOCATION_QUERY` | "¿Dónde están ubicados?" |
| `HUMAN_SUPPORT` | "Quiero hablar con alguien" |
| `GREETING` | "Hola buenos días" |
| `UNKNOWN` | → respuesta de ayuda genérica |

## 🚀 Inicio rápido con Docker

### Windows

```bash
# 1. Configurar variables de entorno
copy .env.example .env
# Editar .env con tus credenciales

# 2. Levantar todo
docker-rebuild.cmd

# Ver logs
docker-rebuild.cmd -Logs
```

### Linux/Mac

```bash
cp .env.example .env
# Editar .env con tus credenciales

docker compose up -d --build
```

**Servicios disponibles:**
- 🌐 FastAPI: `http://localhost` | Docs: `http://localhost/docs`
- 🤖 Ollama: `http://localhost:11434`
- 🗄️ PostgreSQL: `localhost:5432`

## Instalación local (desarrollo sin Docker)

```bash
python -m venv venv
.\venv\Scripts\activate          # Windows
# source venv/bin/activate       # Linux/Mac

pip install -r requirements.txt

# Instalar Ollama desde https://ollama.com y descargar modelo:
ollama pull qwen2.5:7b

# Copiar y editar variables de entorno:
cp .env.example .env
# Cambiar OLLAMA_BASE_URL=http://localhost:11434/v1
# Cambiar DATABASE_URL para apuntar a localhost

uvicorn app.main:app --reload
```

Las tablas se crean automáticamente al iniciar.

## Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `OLLAMA_BASE_URL` | URL de la API Ollama | `http://ollama:11434/v1` |
| `OLLAMA_MODEL` | Modelo de texto | `qwen2.5:7b` |
| `OLLAMA_VISION_MODEL` | Modelo de visión | `llava:7b` |
| `WHATSAPP_TOKEN` | Token Meta Cloud API | `EAAxxxx...` |
| `WHATSAPP_PHONE_NUMBER_ID` | ID del número WhatsApp | `123456789012` |
| `WHATSAPP_VERIFY_TOKEN` | Token de verificación del webhook | `botjuridico_webhook_verify_token_2026` |
| `DATABASE_URL` | Conexión PostgreSQL | `postgresql+asyncpg://...` |
| `ADMIN_API_KEY` | Clave para endpoints `/admin/*` | string seguro |

## Configurar webhook en Meta

1. Exponer públicamente:
   ```bash
   ngrok http 80
   ```

2. Configurar en [Meta Developer Console](https://developers.facebook.com):
   - App → WhatsApp → Configuration → Webhook
   - **Callback URL**: `https://tu-ngrok-url.ngrok.io/webhook`
   - **Verify Token**: valor de `WHATSAPP_VERIFY_TOKEN` en `.env`
   - Subscribe a: `messages`

## Datos de demo

```bash
# Cargar negocio de ejemplo (estudio jurídico)
python seed_demo.py

# Probar pipeline sin WhatsApp
python test_pipeline.py

# Verificar conexión a base de datos
python test_db_connection.py

# Test completo del sistema
python test_system.py
```

## API de administración

Todos los endpoints requieren el header `X-Admin-Key: <ADMIN_API_KEY>`.  
Documentación interactiva completa en `/docs`.

```
POST   /admin/businesses                            Crear negocio
GET    /admin/businesses/{id}/products              Listar productos
POST   /admin/businesses/{id}/products              Crear producto
GET    /admin/businesses/{id}/orders                Ver pedidos
PATCH  /admin/businesses/{id}/orders/{oid}/status   Actualizar estado pedido
GET    /admin/businesses/{id}/bookings              Ver reservas
GET    /admin/businesses/{id}/quotes                Ver cotizaciones
GET    /admin/businesses/{id}/leads                 Ver leads
GET    /admin/businesses/{id}/dashboard             Dashboard resumen
```

## Tipos de mensaje soportados

| Tipo | Procesamiento |
|---|---|
| Texto / botones | Directo al clasificador |
| Audio 🎙️ (OGG/MP3/WAV) | faster-whisper local → texto |
| Imagen 🖼️ (JPEG/PNG/WEBP) | Ollama Vision → descripción de intención |
| PDF 📄 | pypdf → texto extraído |

## Multi-tenant

Una sola instancia soporta **múltiples negocios**. Cada negocio tiene su propio `phone_number_id`, catálogo, pedidos y conversaciones.

## Estructura del proyecto

```
app/
├── ai/
│   ├── intent_classifier.py   # Ollama JSON mode → ExtractedIntent (Pydantic)
│   ├── response_builder.py    # Ollama → texto natural con datos reales
│   └── media_processor.py     # faster-whisper / Ollama Vision / pypdf
├── db/
│   ├── database.py            # Motor async SQLAlchemy
│   └── models.py              # ORM: Business, Product, Order, Booking, Lead…
├── services/
│   ├── products.py / orders.py / bookings.py
│   ├── cart.py / quotes.py / leads.py / handoff.py
│   └── notifications.py
├── routers/
│   ├── webhook.py             # POST /webhook/{phone_number_id}
│   └── admin.py               # Panel admin (API Key protegido)
└── whatsapp/
    ├── gateway.py             # Meta Cloud API — envío de mensajes
    ├── interactive.py         # Botones y listas interactivas
    └── media.py               # Descarga de audio/imagen/PDF
```

## Nichos ideales

- 🍔 Restaurantes y fuentes de soda — menú, precios, pedidos, reservas
- ☕ Cafeterías — carta, horarios, reservas de mesa
- 🔧 Talleres mecánicos — cotizaciones, agendamiento
- 🏥 Clínicas — agendar horas, precios de consultas
- 🏪 Tiendas — stock, precios, pedidos delivery
- 🏗️ Constructoras — cotizaciones, disponibilidad de materiales
- ⚖️ Estudios jurídicos — consultas legales, agendamiento, cotizaciones

## 📦 Despliegue en Railway

**📖 Ver guía completa:** [RAILWAY_SETUP.md](RAILWAY_SETUP.md)

### Resumen rápido:

1. **Base de datos:** Ejecutar `railway-init.sql` en Railway Console
2. **Verificar:** `test.cmd -Db` (con DATABASE_URL de Railway en `.env`)
3. **Ollama:** Servidor externo (VPS o ngrok)
4. **Deploy:** GitHub → Railway (detecta Dockerfile automáticamente)
5. **Variables:** Ver `.env.railway.example`
6. **Webhook:** Configurar en Meta Developer Console

## Licencia

MIT
