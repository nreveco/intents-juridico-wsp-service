# WhatsApp AI Automation Engine
### Documentación Técnica Completa — v1.1 (Days 1–3)

> Motor de automatización WhatsApp + IA para PyMEs.  
> Atiende clientes 24/7 con respuestas inteligentes, carrito de compras,  
> reservas, cotizaciones, transcripción de voz e interpretación de imágenes y PDFs.  
> **100% local — sin costos de API.** Usa Ollama (LLM local) + faster-whisper.

---

## Índice

1. [Arquitectura del sistema](#1-arquitectura-del-sistema)
2. [Flujo principal de un mensaje](#2-flujo-principal-de-un-mensaje)
3. [Estructura del proyecto](#3-estructura-del-proyecto)
4. [Requisitos previos](#4-requisitos-previos)
5. [Configuración de servicios externos](#5-configuración-de-servicios-externos)
   - 5.1 [Ollama (LLM local)](#51-ollama-llm-local)
   - 5.2 [Meta / WhatsApp Business](#52-meta--whatsapp-business)
6. [Instalación paso a paso](#6-instalación-paso-a-paso)
   - 6.1 [Opción A — Local (desarrollo)](#61-opción-a--local-desarrollo)
   - 6.2 [Opción B — Docker (recomendado)](#62-opción-b--docker-recomendado)
7. [Variables de entorno](#7-variables-de-entorno)
8. [Configurar el Webhook en Meta](#8-configurar-el-webhook-en-meta)
9. [Exponer el servidor con ngrok (desarrollo)](#9-exponer-el-servidor-con-ngrok-desarrollo)
10. [Inicializar datos de demo](#10-inicializar-datos-de-demo)
11. [API de administración](#11-api-de-administración)
12. [Intenciones soportadas](#12-intenciones-soportadas)
13. [Tipos de mensajes soportados](#13-tipos-de-mensajes-soportados)
14. [Flujos detallados por funcionalidad](#14-flujos-detallados-por-funcionalidad)
15. [Modelo de base de datos](#15-modelo-de-base-de-datos)
16. [Solución de problemas](#16-solución-de-problemas)

---

## 1. Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENTE (WhatsApp)                           │
│          texto │ voz 🎙️ │ imagen 🖼️ │ PDF 📄 │ botones ⬛         │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    META CLOUD API (Graph v19.0)                     │
│              Recibe, valida y reenvía mensajes vía webhook          │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ POST /webhook/{phone_number_id}
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FASTAPI  —  WhatsApp AI Automation Engine              │
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────────┐ │
│  │  webhook.py  │──▶│  AI Pipeline │──▶│   Intent Router         │ │
│  │  (parser)    │   │              │   │   (services layer)      │ │
│  └──────────────┘   │ 1. Whisper   │   │                         │ │
│                     │    (voz→txt) │   │  products / orders      │ │
│                     │ 2. Vision    │   │  bookings / quotes      │ │
│                     │    (img→txt) │   │  cart / handoff         │ │
│                     │ 3. pypdf     │   │  notifications          │ │
│                     │    (pdf→txt) │   └──────────┬──────────────┘ │
│                     │ 4. Ollama    │              │                │ │
│                     │    classifier│              ▼                │ │
│                     │ 5. Ollama    │   ┌──────────────────────┐   │ │
│                     │    responder │   │   PostgreSQL DB       │   │ │
│                     └──────────────┘   │   (conversations,    │   │ │
│                                        │    orders, leads…)   │   │ │
│                     ┌──────────────┐   └──────────────────────┘   │ │
│                     │  admin.py    │                               │ │
│                     │  REST API    │   ┌──────────────────────┐   │ │
│                     │  /admin/*    │   │  Interactive msgs     │   │ │
│                     └──────────────┘   │  buttons / lists     │   │ │
│                                        └──────────────────────┘   │ │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            │ Respuesta WhatsApp
                            ▼
                    CLIENTE (WhatsApp)
```

### Componentes clave

| Componente | Tecnología | Rol |
|---|---|---|
| API Server | FastAPI 0.115 + uvicorn | Recibe webhooks, expone admin REST |
| Base de datos | PostgreSQL 16 + SQLAlchemy async | Persistencia multi-tenant |
| LLM local | Ollama + qwen2.5:7b / llama3.2:3b | Clasificador de intenciones + generador de respuestas |
| Transcripción de voz | faster-whisper (CPU, modelo `base`) | OGG/MP3/WAV → texto, sin API externa |
| Visión de imágenes | Ollama Vision (llava:7b) | Imagen → descripción de intención |
| Extracción de PDF | pypdf 4 | PDF → texto plano |
| WhatsApp | Meta Cloud API v19.0 | Envío/recepción de mensajes e interactivos |

---

## 2. Flujo principal de un mensaje

```
Cliente envía mensaje
         │
         ▼
┌─────────────────┐
│ ¿Qué tipo es?   │
└────┬────┬───────┘
     │    │
   texto  │ audio ──► faster-whisper (local) ──► texto transcripto
  /botón  │
     │    │ imagen ──► Ollama Vision (llava:7b) ──► descripción de intención
     │    │
     │    │ PDF ──► pypdf ──► texto extraído
     │    │
     └────┘
         │ message_text (siempre texto plano)
         ▼
┌─────────────────────────────────────────────────────┐
│  PASO 1  ·  Clasificador IA (Ollama — qwen2.5:7b)   │
│                                                     │
│  Input:  message_text + historial (últimas 4 turns) │
│          + nombre negocio + categorías              │
│                                                     │
│  Output: ExtractedIntent {                          │
│    intent: PRICE_QUERY | ORDER_CREATE | BOOKING…    │
│    product_name, quantity, service,                 │
│    datetime_requested, quote_description            │
│  }  — via JSON mode + Pydantic validate             │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  PASO 2  ·  Intent Router (Python puro)             │
│                                                     │
│  Ejecuta la lógica real:                            │
│  · Consulta DB (productos, stock, órdenes…)         │
│  · Crea registros (pedido, reserva, cotización…)    │
│  · Gestiona carrito en context JSON                 │
│  · Envía notificación al dueño si aplica            │
│  · ¿Mensaje interactivo? → envía botones/lista      │
│                                                     │
│  Retorna: (query_result: dict, interactive_sent: bool) │
└───────────────────────┬─────────────────────────────┘
                        │  interactive_sent = False
                        ▼
┌─────────────────────────────────────────────────────┐
│  PASO 3  ·  Constructor de respuesta (Ollama)       │
│                                                     │
│  Input:  intent + query_result (datos reales DB)    │
│          + nombre negocio + historial               │
│                                                     │
│  Output: Texto natural en español, amigable         │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  PASO 4  ·  Enviar por WhatsApp                     │
│  · send_text_message() o botones interactivos       │
│  · Guardar en DB (outbound Message)                 │
│  · Actualizar historial conversación (últimos 8)    │
└─────────────────────────────────────────────────────┘
```

---

## 3. Estructura del proyecto

```
24challenge/
│
├── app/
│   ├── main.py                  ← FastAPI app + lifespan (init DB)
│   ├── config.py                ← Pydantic Settings (lee .env)
│   │
│   ├── db/
│   │   ├── database.py          ← Engine async, get_db, init_db
│   │   └── models.py            ← Todos los modelos ORM SQLAlchemy
│   │
│   ├── models/
│   │   └── schemas.py           ← Schemas Pydantic para admin API
│   │
│   ├── intents/
│   │   └── definitions.py       ← Enum Intent + ExtractedIntent (15 intents)
│   │
│   ├── prompts/
│   │   └── templates.py         ← System prompts para clasificador y responder
│   │
│   ├── ai/
│   │   ├── intent_classifier.py ← Ollama JSON mode → ExtractedIntent (Pydantic)
│   │   ├── response_builder.py  ← Ollama → texto de respuesta natural
│   │   └── media_processor.py   ← faster-whisper (voz) / Ollama Vision (img) / pypdf (PDF)
│   │
│   ├── services/
│   │   ├── products.py          ← Búsqueda de productos, menú por categoría
│   │   ├── orders.py            ← Crear pedido, consultar estado
│   │   ├── bookings.py          ← Crear reserva
│   │   ├── leads.py             ← Registro idempotente de leads
│   │   ├── quotes.py            ← Crear solicitud de cotización
│   │   ├── cart.py              ← Carrito multi-ítem (en context JSON)
│   │   ├── handoff.py           ← Transferir a humano
│   │   └── notifications.py     ← Alertas WA al dueño del negocio
│   │
│   ├── whatsapp/
│   │   ├── gateway.py           ← send_text_message, mark_as_read
│   │   ├── interactive.py       ← Botones, listas, bienvenida, catálogo
│   │   └── media.py             ← Descarga de audio/imagen/PDF desde Meta
│   │
│   └── routers/
│       ├── webhook.py           ← POST/GET /webhook/{phone_number_id}
│       └── admin.py             ← REST API /admin/* (protegida con API key)
│
├── seed_demo.py                 ← Carga datos de prueba (restaurante demo)
├── test_pipeline.py             ← Tests del pipeline completo
├── requirements.txt             ← Dependencias Python
├── Dockerfile
├── docker-compose.yml
├── .env.example                 ← Plantilla de variables de entorno
└── .env                        ← TU configuración (NO subir a git)
```

---

## 4. Requisitos previos

### Software necesario

| # | Requisito | Versión mínima | Descarga |
|---|---|---|---|
| 1 | **Python** | 3.11+ | https://python.org/downloads |
| 2 | **Docker Desktop** | 4.x | https://www.docker.com/products/docker-desktop |
| 3 | **PostgreSQL** *(solo opción A local)* | 14+ | https://www.postgresql.org/download |
| 4 | **ngrok** *(solo desarrollo)* | 3.x | https://ngrok.com/download |
| 5 | **Git** | cualquier | https://git-scm.com |

> **Nota:** La opción B (Docker Compose) levanta PostgreSQL y Ollama automáticamente — no requiere instalarlos por separado.

### Cuentas necesarias

| Servicio | Costo | Para qué |
|---|---|---|
| **Meta for Developers** | Gratis | WhatsApp Cloud API |
| **WhatsApp Business Account** | Gratis | Número de teléfono verificado |
| **ngrok** *(dev)* | Gratis (plan básico) | Exponer localhost a internet |

> No se requiere cuenta de OpenAI ni ninguna API de pago. El LLM y la transcripción de audio corren completamente en local.

---

## 5. Configuración de servicios externos

### 5.1 Ollama (LLM local)

Ollama corre dentro del stack de Docker Compose — no requiere configuración manual adicional.
Al primer `docker compose up`, el servicio `ollama-init` descarga el modelo automáticamente.

```
Modelos soportados (configurar con OLLAMA_MODEL en .env):

┌─────────────────┬──────────────┬───────────────────────────────────────┐
│ Modelo          │ Tamaño disco │ Descripción                           │
├─────────────────┼──────────────┼───────────────────────────────────────┤
│ qwen2.5:7b      │ ~4.7 GB      │ Recomendado — excelente en español    │
│ llama3.2:3b     │ ~2.0 GB      │ Más rápido, menos RAM, buen español   │
└─────────────────┴──────────────┴───────────────────────────────────────┘

Modelo de visión (OLLAMA_VISION_MODEL):
┌─────────────────┬──────────────┬───────────────────────────────────────┐
│ llava:7b        │ ~4.7 GB      │ Por defecto para análisis de imágenes │
└─────────────────┴──────────────┴───────────────────────────────────────┘

Transcripción de voz:
  faster-whisper modelo 'base' corre en CPU dentro del contenedor de la app.
  Se descarga automáticamente en el primer arranque (~145 MB).

Costo total de IA: $0.00
```

> Para cambiar el modelo al iniciar:
> ```bash
> OLLAMA_MODEL=llama3.2:3b docker compose up -d
> ```

### 5.2 Meta / WhatsApp Business

```
PASO A — Crear aplicación Meta

1. Ir a https://developers.facebook.com
   └── Clic en "Mis Apps" → "Crear app"
   └── Tipo: "Empresa"
   └── Nombre: "WA Automation Engine" (o el que prefieras)

2. En el panel de la app:
   └── Agregar producto: "WhatsApp"
   └── Seguir el asistente de configuración

──────────────────────────────────────────────────────────────

PASO B — Obtener Phone Number ID y Token temporal

En el panel de WhatsApp → "Comenzar":

┌─────────────────────────────────────────────────────────────┐
│  From: [número de prueba Meta]  ← Phone Number ID aquí     │
│  To: [tu número personal]      ← Para recibir mensajes test│
│                                                             │
│  Temporary access token: EAAxxxx...  ← Copiar este token   │
│  Phone Number ID: 123456789012       ← Copiar este ID      │
└─────────────────────────────────────────────────────────────┘

   ⚠️  El token temporal expira en 24 horas.
       Para producción, generar un token permanente con
       una App de Sistema (System User) en Meta Business.

──────────────────────────────────────────────────────────────

PASO C — Configurar el Webhook (ver Sección 8)

──────────────────────────────────────────────────────────────

PASO D — Agregar número de prueba

WhatsApp → Configuración → Números de teléfono:
└── "Agregar número de teléfono"
└── Verificar con código SMS
└── Este número recibirá mensajes reales

──────────────────────────────────────────────────────────────

PASO E — Token permanente (producción)

1. Meta Business Suite → https://business.facebook.com
2. Configuración → Usuarios del sistema
3. Crear "Usuario del sistema de administrador"
4. Asignar el activo: tu App de WhatsApp
5. Permisos: whatsapp_business_messaging, whatsapp_business_management
6. "Generar token" → nunca expira
```

---

## 6. Instalación paso a paso

### 6.1 Opción A — Local (desarrollo)

Requiere: Python 3.11+, PostgreSQL corriendo, y Ollama instalado en el host.

```bash
# ── 1. Clonar el proyecto ─────────────────────────────────────────
git clone https://github.com/nreveco/wsp-engiener-intents-response-ia.git
cd wsp-engiener-intents-response-ia

# ── 2. Crear entorno virtual Python ───────────────────────────────
python -m venv venv

# Activar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activar (Mac/Linux)
source venv/bin/activate

# ── 3. Instalar dependencias ───────────────────────────────────────
pip install -r requirements.txt
# Incluye: fastapi, openai (cliente compatible Ollama), pypdf, faster-whisper

# ── 4. Instalar Ollama y descargar modelo ─────────────────────────
# Descargar desde https://ollama.com
# Luego:
ollama pull qwen2.5:7b       # modelo principal (~4.7 GB)
ollama pull llava:7b          # modelo de visión opcional (~4.7 GB)
# O el modelo más liviano:
# ollama pull llama3.2:3b

# ── 5. Crear la base de datos (PostgreSQL) ────────────────────────
# psql -U postgres
# CREATE DATABASE automation_db;
# \q

# ── 6. Copiar y editar variables de entorno ────────────────────────
copy .env.example .env
# Abrir .env y completar los valores (ver Sección 7)

# ── 7. Ejecutar el servidor ────────────────────────────────────────
uvicorn app.main:app --reload --port 8000

# El servidor crea las tablas automáticamente al iniciar.
# Debe mostrar:
#   INFO:     Iniciando — creando tablas en base de datos...
#   INFO:     Base de datos lista ✓
#   INFO:     Uvicorn running on http://127.0.0.1:8000

# ── 8. Verificar ──────────────────────────────────────────────────
# http://localhost:8000/docs  → Swagger UI
```

### 6.2 Opción B — Docker (recomendado)

Todo el stack en un comando: app + PostgreSQL + Ollama + descarga automática del modelo.

```bash
# ── 1. Prerequisito: Docker Desktop corriendo ─────────────────────

# ── 2. Clonar el proyecto ─────────────────────────────────────────
git clone https://github.com/nreveco/wsp-engiener-intents-response-ia.git
cd wsp-engiener-intents-response-ia

# ── 3. Copiar y editar variables de entorno ────────────────────────
copy .env.example .env
# Editar .env (solo necesitas whatsapp tokens — no API key de IA)

# ── 4. Elegir modelo y levantar todo ──────────────────────────────
# Con qwen2.5:7b (default, ~4.7 GB, recomendado):
docker compose up -d

# Con llama3.2:3b (más rápido y liviano, ~2 GB):
OLLAMA_MODEL=llama3.2:3b docker compose up -d

# Primera vez:
#   - Descarga ollama/ollama:latest
#   - Construye la imagen de la app
#   - El servicio ollama-init descarga el modelo LLM (~2-5 min según conexión)
# Siguientes veces: arranque instantáneo (modelo ya en volumen ollama_data)

# ── 5. Verificar ──────────────────────────────────────────────────
docker compose logs -f ollama-init   # ver progreso de descarga del modelo
docker compose logs -f app           # ver logs de la aplicación
# http://localhost:8000/docs  → Swagger UI

# ── 6. Detener (mantiene datos y modelo) ─────────────────────────
docker compose down

# ── 7. Detener y borrar todo (incluye modelo descargado) ─────────
docker compose down -v
```

> **Tip:** Si ya tenés Ollama instalado en el host con los modelos descargados,
> podés evitar la re-descarga usando un bind-mount en `docker-compose.yml`:
> ```yaml
> volumes:
>   - "C:/Users/TU_USUARIO/.ollama:/root/.ollama"
> ```

---

## 7. Variables de entorno

Editar el archivo `.env` con los valores reales:

```env
# ── Ollama (LLM local) ───────────────────────────────────────────
# En Docker:  http://ollama:11434/v1  (nombre del servicio en compose)
# En local:   http://localhost:11434/v1
OLLAMA_BASE_URL=http://ollama:11434/v1

# Modelo de texto: qwen2.5:7b (recomendado) o llama3.2:3b (más liviano)
OLLAMA_MODEL=qwen2.5:7b

# Modelo de visión (para análisis de imágenes)
OLLAMA_VISION_MODEL=llava:7b

# ── Meta Cloud API ───────────────────────────────────────────────
# Phone Number ID: panel WhatsApp → "From" (número de prueba)
WHATSAPP_PHONE_NUMBER_ID=123456789012345

# Token: panel WhatsApp → "Temporary access token" (o token permanente)
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Verify Token: CUALQUIER string secreto que tú elijas
# Lo necesitarás al configurar el webhook en Meta (Sección 8)
WHATSAPP_VERIFY_TOKEN=mi_secreto_super_seguro_2024

# ── Base de datos ────────────────────────────────────────────────
# Local:  postgresql+asyncpg://postgres:TU_PASS@localhost:5432/automation_db
# Docker: postgresql+asyncpg://postgres:postgres@db:5432/automation_db
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/automation_db

# ── Admin API ────────────────────────────────────────────────────
# Clave secreta para proteger los endpoints /admin/*
# Úsala como header: X-Admin-Key: tu_clave_aqui
ADMIN_API_KEY=clave_admin_super_segura_2024

# ── App ──────────────────────────────────────────────────────────
DEBUG=false
ENVIRONMENT=production
```

> **Seguridad:** Nunca subas `.env` a GitHub. Ya está en `.gitignore`.

---

## 8. Configurar el Webhook en Meta

El webhook es la URL donde Meta enviará todos los mensajes de WhatsApp.

```
Diagrama de verificación del webhook:

Tu código                Meta Developers
    │                         │
    │  ◄── GET /webhook/ID ───┤  Con:
    │       ?hub.mode=subscribe  hub.verify.token=TU_VERIFY_TOKEN
    │       ?hub.challenge=12345 hub.challenge=número_aleatorio
    │                         │
    │  if verify_token == OK  │
    │  return hub.challenge   │
    │  ────────────────────►  │
    │                         │  ✓ Webhook verificado
```

### Pasos en el panel de Meta

```
1. Ir a: developers.facebook.com → Tu App → WhatsApp → Configuración

2. En "Webhook" clic en "Editar":

   URL de devolución de llamada:
   https://TU_DOMINIO/webhook/PHONE_NUMBER_ID
   
   Ejemplo con ngrok:
   https://abc123.ngrok-free.app/webhook/123456789012345
   
   Token de verificación:
   mi_secreto_super_seguro_2024   ← mismo valor que WHATSAPP_VERIFY_TOKEN

3. Clic "Verificar y guardar"
   └── Meta hará GET a tu URL, tu servidor responderá con el challenge
   └── Si aparece ✓ verde: webhook configurado correctamente

4. Suscribir a eventos:
   └── messages  ✓  (obligatorio)
   └── message_echoes  (opcional, para ver copias de mensajes enviados)
```

---

## 9. Exponer el servidor con ngrok (desarrollo)

Para que Meta pueda alcanzar tu servidor local durante el desarrollo.

```bash
# ── 1. Instalar ngrok ─────────────────────────────────────────────
# Descargar desde https://ngrok.com/download
# O con winget:
winget install ngrok

# ── 2. Autenticar ngrok (una sola vez) ───────────────────────────
# Ir a https://dashboard.ngrok.com/get-started/your-authtoken
# Copiar el authtoken y ejecutar:
ngrok config add-authtoken TU_AUTHTOKEN_AQUI

# ── 3. Exponer el puerto 8000 ─────────────────────────────────────
ngrok http 8000

# Mostrará algo así:
#
#  Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
#
# Copiar la URL https://abc123.ngrok-free.app

# ── 4. Flujo completo desarrollo ──────────────────────────────────
#
#  Terminal 1: uvicorn app.main:app --reload --port 8000
#  Terminal 2: ngrok http 8000
#
#  Webhook URL en Meta: https://abc123.ngrok-free.app/webhook/{PHONE_NUMBER_ID}
#
#  ⚠️  La URL de ngrok cambia cada vez que reinicias (plan gratuito).
#      Plan gratuito de ngrok te permite un dominio estático con la cuenta.
```

### Diagrama de desarrollo local

```
WhatsApp ──► Meta Cloud ──► ngrok ──► localhost:8000 ──► FastAPI ──► PostgreSQL
                            tunnel     (tu PC)
```

---

## 10. Inicializar datos de demo

Carga un restaurante de prueba completo con productos y categorías.

```bash
# (con venv activado y servidor corriendo)
python seed_demo.py

# Mostrará:
# ⚙️  Creando tablas...
# ✅ Negocio creado: Fuente de Soda El Rancho  (ID: xxx)
# ✅ Categorías: Bebidas, Platos Principales, Postres...
# ✅ Productos: Hamburguesa Clásica $8.990, etc.

# ⚠️  IMPORTANTE: después de seed_demo.py, actualizar el negocio
# con tu Phone Number ID y Token REALES usando el admin API:

curl -X PATCH http://localhost:8000/admin/businesses/{business_id} \
  -H "X-Admin-Key: TU_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number_id": "TU_PHONE_NUMBER_ID_REAL",
    "whatsapp_token": "TU_TOKEN_REAL"
  }'
```

---

## 11. API de administración

Todas las rutas requieren el header: `X-Admin-Key: TU_ADMIN_API_KEY`

Documentación interactiva completa en: `http://localhost:8000/docs`

### Endpoints principales

```
── Negocios ──────────────────────────────────────────────────────────
POST   /admin/businesses                    Crear negocio
GET    /admin/businesses                    Listar negocios
GET    /admin/businesses/{id}               Ver negocio
PATCH  /admin/businesses/{id}               Actualizar negocio

── Catálogo ──────────────────────────────────────────────────────────
POST   /admin/businesses/{id}/categories    Crear categoría
GET    /admin/businesses/{id}/categories    Listar categorías
POST   /admin/businesses/{id}/products      Crear producto
GET    /admin/businesses/{id}/products      Listar productos
PATCH  /admin/businesses/{id}/products/{pid} Actualizar/desactivar producto

── Pedidos ───────────────────────────────────────────────────────────
GET    /admin/businesses/{id}/orders        Ver todos los pedidos
PATCH  /admin/businesses/{id}/orders/{oid}/status  Actualizar estado pedido

── Reservas ──────────────────────────────────────────────────────────
GET    /admin/businesses/{id}/bookings      Ver reservas
PATCH  /admin/businesses/{id}/bookings/{bid}/status  Confirmar/cancelar

── Cotizaciones ──────────────────────────────────────────────────────
GET    /admin/businesses/{id}/quotes                    Listar cotizaciones
GET    /admin/businesses/{id}/quotes/{qid}              Ver cotización
POST   /admin/businesses/{id}/quotes/{qid}/items        Agregar ítem con precio
PATCH  /admin/businesses/{id}/quotes/{qid}/status       Cambiar estado

── Leads / Conversaciones ───────────────────────────────────────────
GET    /admin/businesses/{id}/leads         Todos los leads
GET    /admin/businesses/{id}/conversations Ver conversaciones
GET    /admin/businesses/{id}/conversations/{cid}/messages  Historial
PATCH  /admin/businesses/{id}/conversations/{cid}/close    Cerrar handoff

── Dashboard y Analytics ────────────────────────────────────────────
GET    /admin/businesses/{id}/dashboard     Resumen general
GET    /admin/businesses/{id}/analytics?period=day|week|month  Analytics
```

### Ejemplo: crear un negocio

```bash
curl -X POST http://localhost:8000/admin/businesses \
  -H "X-Admin-Key: TU_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Restaurante",
    "phone_number_id": "123456789012345",
    "whatsapp_token": "EAAxxxx...",
    "business_type": "restaurant",
    "welcome_message": "¡Hola! Bienvenido a Mi Restaurante 🍽️",
    "human_support_phone": "+56912345678",
    "address": "Av. Principal 123",
    "city": "Santiago",
    "currency_symbol": "$",
    "hours": {
      "lunes": "12:00-22:00",
      "martes": "12:00-22:00",
      "miercoles": "12:00-22:00",
      "jueves": "12:00-22:00",
      "viernes": "12:00-23:00",
      "sabado": "12:00-23:00",
      "domingo": "12:00-21:00"
    }
  }'
```

---

## 12. Intenciones soportadas

El sistema reconoce automáticamente 15 intenciones en lenguaje natural:

| Intent | Ejemplos de mensajes |
|---|---|
| `GREETING` | "Hola", "Buenos días", "Buenas tardes" |
| `PRICE_QUERY` | "¿Cuánto cuesta la hamburguesa?", "Precio del corte de pelo" |
| `PRODUCT_INFO` | "¿Qué productos tienen?", "Muéstrame el menú" |
| `ORDER_CREATE` | "Quiero pedir una pizza", "Dame 2 hamburguesas" |
| `ORDER_STATUS` | "¿Cómo va mi pedido?", "Estado de mi orden" |
| `BOOKING` | "Quiero reservar para 2 personas el viernes a las 8" |
| `QUOTE_REQUEST` | "Necesito cotización para pintar mi auto", "¿Cuánto cuesta...?" |
| `CART_ADD` | "Agrega una Coca-Cola", "Añade 2 papas fritas" |
| `CART_VIEW` | "¿Qué tengo en el carrito?", "Ver mi pedido" |
| `CART_CHECKOUT` | "Confirmar pedido", "Listo, ese es mi pedido" |
| `CART_CLEAR` | "Cancelar", "Vaciar carrito", "Empezar de nuevo" |
| `HOURS_QUERY` | "¿A qué hora abren?", "¿Cuál es el horario?" |
| `LOCATION_QUERY` | "¿Dónde están?", "Dirección", "¿Cómo llego?" |
| `HUMAN_SUPPORT` | "Necesito hablar con alguien", "Tengo un problema" |
| `UNKNOWN` | Cualquier mensaje no reconocido → respuesta de ayuda genérica |

---

## 13. Tipos de mensajes soportados

```
Tipo WhatsApp     Procesamiento                       Resultado
─────────────────────────────────────────────────────────────────────
text              Directo al clasificador IA          Normal

interactive       Mapeo de button_id → texto          Normal
(botones/listas)  acción_menu → "ver el menú"

audio 🎙️          faster-whisper (local, CPU)         Texto transcripto
  OGG/MP3/WAV     modelo 'base', idioma "es"          → clasificador IA
  M4A/WEBM/FLAC   sin costo, sin API externa
                  Si falla: pide escribir consulta

image 🖼️          Ollama Vision (llava:7b)            Descripción de intención
  JPEG/PNG/GIF    caption + análisis de imagen        → clasificador IA
  WEBP            API compatible OpenAI, local
                  Si falla: pide descripción texto

document 📄       Solo PDFs aceptados                 Texto extraído (3000 chars)
  PDF             pypdf extractor                     → clasificador IA
                  Si vacío: pide descripción texto
```

---

## 14. Flujos detallados por funcionalidad

### Flujo: Pedido con carrito

```
Cliente: "Quiero una hamburguesa"
  → CART_ADD → busca "hamburguesa" en DB ✓
  → Agrega a context["cart"]
  → Envía botones interactivos:
    ┌─────────────────────────────┐
    │ 🛒 Tu pedido:               │
    │ • Hamburguesa x1  $8.990   │
    │ Total: $8.990               │
    │                             │
    │ [✅ Confirmar] [➕ Agregar] [❌ Cancelar] │
    └─────────────────────────────┘

Cliente: "Agrega una Coca-Cola"
  → CART_ADD → agrega a carrito
  → Muestra carrito actualizado con botones

Cliente: [toca "✅ Confirmar"]
  → button_id "confirm_order" → "confirmar pedido"
  → CART_CHECKOUT → crea Order + OrderItems en DB
  → Notifica al dueño por WhatsApp
  → Respuesta: "✅ Pedido #XYZ confirmado..."
```

### Flujo: Reserva

```
Cliente: "Quiero reservar para 2 el viernes"
  → BOOKING → IA extrae datetime_requested="viernes"
  → Crea Booking (status: PENDING) en DB
  → Notifica al dueño: "📅 Nueva reserva de [cliente]"
  → Respuesta: "✅ Reserva recibida para el viernes. Te confirmaremos pronto."

Dueño: PATCH /admin/businesses/{id}/bookings/{bid}/status
  → {"status": "confirmed"}
  → (futuro: notificar al cliente)
```

### Flujo: Cotización

```
Cliente: "Necesito presupuesto para tapicería de mi auto"
  → QUOTE_REQUEST → crea Quote (status: draft) en DB
  → Notifica al dueño con descripción
  → Respuesta: "📋 Cotización #Q-XYZ registrada. Te contactaremos pronto."

Dueño admin:
  POST /admin/.../quotes/{id}/items  → agrega ítems con precios
  PATCH /admin/.../quotes/{id}/status → {"status": "sent"}
```

### Flujo: Mensaje de voz

```
Cliente: 🎙️ [nota de voz: "quiero saber el precio del menú ejecutivo"]
    │
    ▼
download_media() → audio bytes (OGG)
    │
    ▼
faster-whisper (local, CPU, modelo 'base')
  → "quiero saber el precio del menú ejecutivo"
  → sin API, sin costo, ~1-3s en CPU
    │
    ▼
→ PRICE_QUERY → busca "menú ejecutivo" en DB
    │
    ▼
→ Respuesta normal con precio
```

### Flujo: Handoff a humano

```
Cliente: "Quiero hablar con una persona"
  → HUMAN_SUPPORT
  → conversation.status = HUMAN_HANDOFF (bot deja de responder)
  → Notifica al dueño: "👨‍💼 [cliente] solicita atención humana"
  → Respuesta: "Te conectamos con nuestro equipo..."

Dueño atiende al cliente directamente en WhatsApp.

Dueño admin: PATCH /admin/.../conversations/{id}/close
  → conversation.status = CLOSED (o ACTIVE para reactivar bot)
```

---

## 15. Modelo de base de datos

```
Business ─────────────────────────────────────────────────────┐
  id, name, phone_number_id, whatsapp_token                   │
  business_type, welcome_message, human_support_phone         │
  is_active                                                    │
      │                                                        │
      ├──► BusinessSettings                                    │
      │      currency_symbol, address, city, maps_url, hours  │
      │                                                        │
      ├──► Category ──► Product                               │
      │      name           name, price, description           │
      │                     category_id, is_available          │
      │                                                        │
      ├──► Conversation                                        │
      │      customer_phone, customer_name                     │
      │      status: ACTIVE | HUMAN_HANDOFF | CLOSED           │
      │      context: {"history": [...], "cart": [...]}        │
      │          │                                             │
      │          └──► Message                                  │
      │                 direction: inbound | outbound          │
      │                 content, intent, wa_message_id         │
      │                                                        │
      ├──► Order ──► OrderItem                                │
      │      customer_phone, total                             │
      │      status: PENDING|CONFIRMED|PREPARING|READY|DONE   │
      │                                                        │
      ├──► Booking                                             │
      │      customer_phone, service, datetime_requested       │
      │      status: PENDING | CONFIRMED | CANCELLED           │
      │                                                        │
      ├──► Lead                                               │
      │      phone, name, first_intent, created_at            │
      │                                                        │
      └──► Quote ──► QuoteItem                               │
             customer_phone, description, total               │
             status: DRAFT | SENT | ACCEPTED | REJECTED       │
```

---

## 16. Solución de problemas

### El servidor no inicia

```
Error: connection refused (PostgreSQL)
→ En Docker: verificar que el servicio db está healthy
    docker compose ps
→ En local: verificar que PostgreSQL está corriendo y automation_db existe
→ Verificar DATABASE_URL en .env

Error: connection refused (Ollama)
→ En Docker: el servicio ollama puede estar aún descargando el modelo
    docker compose logs ollama-init   ← ver progreso
→ En local: verificar que ollama está corriendo en localhost:11434
    ollama list   ← debe mostrar el modelo descargado
→ Verificar OLLAMA_BASE_URL en .env
```

### El webhook no verifica

```
Error 403 en Meta al guardar webhook
→ Verificar que WHATSAPP_VERIFY_TOKEN en .env coincide 
  exactamente con el "Token de verificación" ingresado en Meta
→ Verificar que ngrok está corriendo y la URL es correcta
→ Probar manualmente:
  curl "https://TU_NGROK.ngrok-free.app/webhook/ID?hub.mode=subscribe&hub.challenge=test&hub.verify.token=TU_TOKEN"
  → Debe responder con: test
```

### Los mensajes llegan pero no hay respuesta

```
1. Revisar logs del servidor: verás el pipeline completo
     docker compose logs -f app
2. Verificar que el business.phone_number_id en DB coincide 
   con el phone_number_id en la URL del webhook
3. Verificar que Ollama está healthy y el modelo está cargado:
     docker compose ps
     docker compose logs ollama
4. Verificar que el token de WhatsApp no expiró (token temporal = 24h)
5. Si el intent classifier falla → el log mostrará el JSON crudo de Ollama;
   puede indicar que el modelo no generó JSON válido:
     docker compose logs app | grep "Error clasificando"
```

### Error al procesar audio

```
Error faster-whisper: "No such file or directory" o "ffmpeg not found"
→ El contenedor de la app necesita ffmpeg para convertir audio OGG
→ Verificar que el Dockerfile incluye: RUN apt-get install -y ffmpeg
→ O cambiar modelo de faster-whisper a 'base' que soporta OGG nativo

Error faster-whisper: descarga lenta al primer arranque
→ El modelo 'base' (~145 MB) se descarga en el primer transcribe()
→ Normal — los siguientes mensajes de voz son inmediatos (modelo cacheado)
```

### Error al procesar imágenes

```
Error Vision: "model not found" o timeout
→ El modelo de visión (llava:7b) debe descargarse por separado:
     docker compose exec ollama ollama pull llava:7b
→ Si no necesitás análisis de imágenes, podés ignorar este error;
   el sistema responde solicitando texto al cliente como fallback
```

### Instalar pypdf manualmente

```bash
pip install pypdf==4.3.1

# Verificar:
python -c "import pypdf; print(pypdf.__version__)"
# 4.3.1
```

---

## Checklist de puesta en marcha

```
□ Docker Desktop instalado y corriendo
□ .env creado con:
  □ OLLAMA_BASE_URL=http://ollama:11434/v1
  □ OLLAMA_MODEL=qwen2.5:7b  (o llama3.2:3b)
  □ WHATSAPP_TOKEN
  □ WHATSAPP_PHONE_NUMBER_ID
  □ WHATSAPP_VERIFY_TOKEN (valor que tú eliges)
  □ DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/automation_db
  □ ADMIN_API_KEY
□ docker compose up -d  ejecutado
□ docker compose logs ollama-init  → modelo descargado ✓
□ http://localhost:8000/docs  accesible
□ ngrok http 8000  corriendo
□ Webhook configurado en Meta con URL ngrok
□ Webhook verificado ✓ (palomita verde en Meta)
□ python seed_demo.py  ejecutado (opcional, para demo)
□ Enviar "Hola" desde WhatsApp al número de prueba → ¡funciona! 🎉
```

---

*Documentación generada para el 24-Hour Automation Challenge — v1.1 (migrado a Ollama local)*
