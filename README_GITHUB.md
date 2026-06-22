# 🤖 Bot WhatsApp Jurídico con IA - Mediaciones RJZ

Sistema de automatización inteligente para WhatsApp especializado en **atención legal 24/7** para estudios jurídicos.

Responde consultas, clasifica casos, detecta urgencias y agenda citas automáticamente usando **IA local con Ollama** — sin costos de API.

---

## ✨ Características

- 🤖 **IA Local**: Ollama con modelos `qwen2.5:7b` / `llama3.2:3b`
- ⚖️ **Especializado en Legal**: Derecho Penal, Familia, Civil
- 🚨 **Detección de Urgencias**: Escalamiento automático a abogado
- 📅 **Agendamiento**: Consultas y citas automáticas
- 💬 **Multi-Intents**: 13 intenciones legales especializadas
- 🎙️ **Audio**: Transcripción con `faster-whisper`
- 🖼️ **Imágenes**: Análisis con Ollama Vision
- 📄 **PDFs**: Extracción de texto con `pypdf`
- 🔐 **Seguro**: Disclaimers legales automáticos

---

## 🏗️ Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Backend | FastAPI (async) |
| Base de datos | PostgreSQL 16 + SQLAlchemy |
| LLM | Ollama (`qwen2.5:7b`) |
| Transcripción | faster-whisper (local) |
| Visión | Ollama Vision (`llava:7b`) |
| WhatsApp | Meta Cloud API |
| Deploy | Railway + Docker |

---

## 🚀 Deploy en Railway

### 1. Fork este repositorio

### 2. Crear proyecto en Railway

1. Ir a [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Seleccionar tu fork

### 3. Agregar PostgreSQL

1. En Railway: New → Database → PostgreSQL
2. Railway inyecta automáticamente `DATABASE_URL`

### 4. Configurar Servidor Ollama

**Railway no soporta GPU**, necesitas un servidor externo con Ollama:

**Opciones:**
- VPS con GPU (RunPod, Paperspace, Lambda Labs)
- Servidor local con Cloudflare Tunnel
- ngrok (solo pruebas)

Ver guía completa: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

### 5. Variables de Entorno en Railway

```env
# Ollama (servidor externo)
OLLAMA_BASE_URL=http://TU_IP:11434/v1
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_VISION_MODEL=llava:7b

# WhatsApp Meta Cloud API
WHATSAPP_TOKEN=EAAxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_VERIFY_TOKEN=tu_token_secreto

# Admin
ADMIN_API_KEY=admin_key_secreta

# App
ENVIRONMENT=production
DEBUG=false
```

### 6. Ejecutar Seed

```bash
# Usando Railway CLI
railway run python seed_legal_rzj.py
```

### 7. Configurar Webhook de WhatsApp

1. [developers.facebook.com](https://developers.facebook.com)
2. Tu App → WhatsApp → Webhook
3. URL: `https://tu-app.up.railway.app/webhook/{PHONE_NUMBER_ID}`
4. Verify Token: Mismo de `WHATSAPP_VERIFY_TOKEN`

---

## 💻 Desarrollo Local

### Con Docker (Recomendado)

```bash
git clone https://github.com/nreveco/intents-juridico-wsp-service.git
cd intents-juridico-wsp-service

cp .env.example .env
# Editar .env con tus tokens

docker compose up -d
```

### Sin Docker

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Instalar Ollama: https://ollama.com
ollama pull qwen2.5:7b
ollama pull llava:7b

# Iniciar PostgreSQL
# Editar .env con DATABASE_URL local

uvicorn app.main:app --reload
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

---

## 📋 Intenciones Detectadas

| Intent | Ejemplo | Acción |
|---|---|---|
| `GREETING` | "Hola, quiero información" | Bienvenida |
| `CASE_INQUIRY` | "¿Pueden ayudarme?" | Evaluación inicial |
| `SERVICE_INFO` | "¿Ven temas penales?" | Info de áreas legales |
| `PAYMENT_INFO` | "¿Cuánto cobran?" | Estructura de honorarios |
| `TIMEFRAME_QUERY` | "¿Cuánto demora?" | Info de plazos |
| `BOOKING` | "Quiero agendar consulta" | Agenda cita |
| `QUOTE_REQUEST` | "Necesito cotización" | Genera presupuesto |
| `BENEFIT_INFO` | "¿Beneficios penitenciarios?" | Info legal |
| `LAWYER_IDENTITY` | "¿Con quién hablo?" | Presentación |
| `HUMAN_SUPPORT` | "Hablar con abogado" | Escalamiento |
| `HOURS_QUERY` | "¿Horarios?" | Info de atención |
| `LOCATION_QUERY` | "¿Dónde están?" | Dirección |
| `UNKNOWN` | - | Ayuda general |

---

## 🚨 Detección de Urgencias

El bot detecta automáticamente casos críticos:

```python
# Keywords de urgencia
["detenido", "prisión preventiva", "audiencia hoy", "audiencia mañana"]

# Acción automática:
→ Notifica al abogado inmediatamente
→ Crea caso con prioridad ALTA
→ Responde: "Un abogado te contactará en 15 minutos"
```

---

## 📊 Pipeline de Mensajes

```
WhatsApp (Meta Cloud API)
        │
        ▼
  [1] Media Processor    ← Audio/Imagen/PDF
        │
        ▼
  [2] Intent Classifier  ← Ollama JSON mode
        │
        ▼
  [3] Action Router      ← Lógica de negocio
        │
        ▼
  [4] Response Builder   ← Ollama
        │
        ▼
WhatsApp → Cliente
```

---

## 📄 Documentación

- **[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)** - Guía completa de deploy
- **[RESUMEN_EJECUTIVO_RJZ.md](./RESUMEN_EJECUTIVO_RJZ.md)** - Vista ejecutiva
- **[ANALISIS_ESTUDIO_JURIDICO.md](./ANALISIS_ESTUDIO_JURIDICO.md)** - Diseño técnico
- **[FLUJOS_CONVERSACIONALES_RJZ.md](./FLUJOS_CONVERSACIONALES_RJZ.md)** - Ejemplos

---

## 🔒 Seguridad

- ✅ Disclaimers legales automáticos
- ✅ No almacena confesiones en logs
- ✅ Encriptación de datos sensibles
- ✅ Admin API protegida con API Key
- ✅ Webhook verificado con token

---

## 📈 Casos de Uso

- ⚖️ Estudios jurídicos (Penal, Familia, Civil)
- 🏥 Clínicas médicas (agendamiento)
- 🔧 Talleres mecánicos (cotizaciones)
- 🍔 Restaurantes (pedidos)
- 🏪 Tiendas (catálogo, stock)

---

## 💰 Costos Estimados

**Con Servidor Local:**
- Railway: $20/mes
- Electricidad: ~$25/mes
- **Total:** ~$45/mes

**Con VPS GPU:**
- Railway: $20/mes
- VPS GPU: $200-360/mes
- **Total:** ~$220-380/mes

---

## 🤝 Contribuir

Pull requests son bienvenidos. Para cambios grandes, abre un issue primero.

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/nreveco/intents-juridico-wsp-service/issues)
- **Docs**: Ver carpeta `/docs`

---

## 📜 Licencia

MIT License - Ver [LICENSE](./LICENSE)

---

## 🙏 Créditos

- **Meta Cloud API**: WhatsApp Business
- **Ollama**: LLM local
- **FastAPI**: Framework web
- **faster-whisper**: Transcripción de audio

---

**Desarrollado para Mediaciones RJZ** ⚖️
