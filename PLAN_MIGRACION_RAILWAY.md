# 🚀 PLAN DE MIGRACIÓN Y DEPLOY A RAILWAY

## 📊 RESUMEN EJECUTIVO

### Objetivo
Migrar el bot de WhatsApp jurídico "Mediaciones RJZ" a un nuevo repositorio GitHub y desplegarlo en Railway con Ollama externo.

### ¿Qué se ha preparado?
✅ Dockerfile optimizado para Railway  
✅ Configuración de variables de entorno  
✅ Documentación completa de deploy  
✅ Scripts de migración  
✅ README para GitHub  
✅ .gitignore actualizado  

---

## 📁 ARCHIVOS CREADOS/MODIFICADOS

### ✅ Archivos Nuevos

1. **`Dockerfile.railway`**
   - Dockerfile optimizado para Railway
   - Incluye health check
   - Workers configurados (2)

2. **`.env.railway.example`**
   - Plantilla de variables para Railway
   - Solo con Ollama (servidor externo)
   - Sin OpenAI

3. **`RAILWAY_DEPLOYMENT.md`** (15 KB)
   - Guía completa paso a paso
   - 3 opciones de servidor Ollama
   - Troubleshooting
   - Estimación de costos

4. **`README_GITHUB.md`**
   - README público para GitHub
   - Instrucciones de instalación
   - Features destacadas
   - Badges y documentación

5. **`PUSH_TO_GITHUB.md`**
   - Comandos exactos para subir a GitHub
   - Manejo de autenticación
   - Verificación post-push

6. **`PLAN_MIGRACION_RAILWAY.md`** (este archivo)
   - Resumen completo del plan
   - Checklist de tareas
   - Timeline estimado

7. **`.gitignore`**
   - Ignora archivos sensibles (.env, logs, etc.)
   - Optimizado para Python/Railway

### 📝 Archivos Modificados

1. **`app/config.py`**
   - Agregado `port` field
   - Agregado `is_production` property
   - Soporte para detección de Railway

---

## 🎯 ARQUITECTURA DE DEPLOY

```
┌─────────────────┐
│   WhatsApp      │
│   (Meta Cloud)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│   Railway App   │────▶│  PostgreSQL      │
│   (FastAPI)     │     │  (Railway DB)    │
└────────┬────────┘     └──────────────────┘
         │
         ▼
┌─────────────────┐
│ Servidor Ollama │
│ (GPU - Externo) │
│   qwen2.5:7b    │
│   llava:7b      │
└─────────────────┘
```

### Componentes

| Componente | Hosting | Costo |
|---|---|---|
| **FastAPI Bot** | Railway | $20/mes (Pro) |
| **PostgreSQL** | Railway | Incluido |
| **Ollama + GPU** | VPS o Local | $0-360/mes |

---

## 📋 PLAN DE ACCIÓN (PASO A PASO)

### FASE 1: Preparación Local ✅ COMPLETADO

- [x] Crear `Dockerfile.railway`
- [x] Crear `.env.railway.example`
- [x] Crear `RAILWAY_DEPLOYMENT.md`
- [x] Crear `README_GITHUB.md`
- [x] Crear `PUSH_TO_GITHUB.md`
- [x] Actualizar `.gitignore`
- [x] Modificar `app/config.py`

### FASE 2: Migrar a GitHub (15 minutos)

```powershell
# 1. Eliminar repo anterior
cd d:\bot-jurico\wsp-engiener-intents-response-ia
Remove-Item -Recurse -Force .git

# 2. Crear README principal
Copy-Item README_GITHUB.md README.md

# 3. Inicializar Git
git init
git config user.name "nreveco"
git config user.email "tu-email@example.com"

# 4. Primer commit
git add .
git commit -m "feat: Bot WhatsApp jurídico con IA - Mediaciones RJZ"

# 5. Conectar con GitHub
git branch -M main
git remote add origin https://github.com/nreveco/intents-juridico-wsp-service.git

# 6. Push
git push -u origin main
```

**Verificar:** https://github.com/nreveco/intents-juridico-wsp-service

### FASE 3: Configurar Servidor Ollama (30-60 min)

#### Opción A: VPS con GPU (Recomendado para producción)

**Providers sugeridos:**
- **RunPod**: GPU T4 (~$0.30/h) o RTX 4090 (~$0.50/h)
- **Paperspace**: GPU P4000 (~$0.51/h)
- **Lambda Labs**: GPU RTX 6000 (~$0.50/h)
- **Vast.ai**: Marketplace GPU (desde $0.20/h)

**Setup:**
```bash
# 1. Crear instancia con GPU
# 2. SSH al servidor
ssh user@ip-servidor

# 3. Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 4. Configurar servicio
export OLLAMA_HOST=0.0.0.0:11434

cat > /etc/systemd/system/ollama.service << 'EOF'
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=root
Environment="OLLAMA_HOST=0.0.0.0:11434"
ExecStart=/usr/local/bin/ollama serve
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# 5. Descargar modelos (esto toma ~10 min)
ollama pull qwen2.5:7b
ollama pull llava:7b

# 6. Abrir firewall
sudo ufw allow 11434/tcp

# 7. Verificar
curl http://localhost:11434/v1/models

# 8. Obtener IP pública
curl ifconfig.me
# Anotar esta IP para Railway
```

#### Opción B: Servidor Local (Gratis, para pruebas)

```powershell
# 1. Asegurar Ollama corriendo
ollama serve

# 2. Instalar Cloudflare Tunnel o ngrok
# ngrok (temporal):
ngrok http 11434

# 3. Copiar URL pública
# Ej: https://abc123.ngrok-free.app
```

### FASE 4: Deploy en Railway (20 minutos)

```bash
# 1. Ir a railway.app
# 2. New Project → Deploy from GitHub
# 3. Autorizar GitHub → Seleccionar: nreveco/intents-juridico-wsp-service
# 4. Railway detecta Dockerfile.railway automáticamente
```

#### Agregar PostgreSQL

1. Click "New" → "Database" → "PostgreSQL"
2. Railway crea automáticamente
3. Variable `DATABASE_URL` se inyecta auto

#### Configurar Variables

En Railway → Variables → Raw Editor:

```env
# Ollama (servidor externo - REEMPLAZAR CON TU IP/URL)
OLLAMA_BASE_URL=http://TU_IP_PUBLICA:11434/v1
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_VISION_MODEL=llava:7b

# WhatsApp (REEMPLAZAR CON TUS TOKENS)
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=mi_token_super_secreto_123

# Admin
ADMIN_API_KEY=admin_clave_secreta_cambiar_esto

# App
ENVIRONMENT=production
DEBUG=false
```

#### Deploy

1. Click "Deploy"
2. Esperar build (~5 min)
3. Obtener URL: `https://intents-juridico-wsp-service.up.railway.app`

### FASE 5: Inicializar Base de Datos (5 minutos)

```bash
# Opción A: Railway CLI
railway login
railway link
railway run python seed_legal_rzj.py

# Opción B: Desde local
# Copiar DATABASE_URL desde Railway
$env:DATABASE_URL="postgresql://postgres:xxxxx@xxxxx.railway.app:5432/railway"
python seed_legal_rzj.py
```

**Verificar:**
```bash
railway run python -c "from app.db.database import SessionLocal; print('DB OK')"
```

### FASE 6: Configurar Webhook WhatsApp (10 minutos)

1. Ir a: https://developers.facebook.com
2. Tu App → WhatsApp → Configuration → Webhooks
3. **Callback URL:** `https://intents-juridico-wsp-service.up.railway.app/webhook/{PHONE_NUMBER_ID}`
4. **Verify Token:** Mismo de `WHATSAPP_VERIFY_TOKEN`
5. Click "Verify and Save"
6. Subscribir a: `messages`

### FASE 7: Testing (15 minutos)

```bash
# 1. Health check
curl https://intents-juridico-wsp-service.up.railway.app/health

# 2. Ver logs
railway logs --follow

# 3. Enviar mensaje de prueba desde WhatsApp
# Al número configurado, enviar: "Hola"

# Respuesta esperada:
# "¡Hola! Bienvenido a Mediaciones RJZ ⚖️
# Somos un estudio jurídico especializado en..."
```

**Casos de prueba:**

| Mensaje | Intent Esperado | Respuesta |
|---|---|---|
| "Hola" | GREETING | Bienvenida |
| "¿Ven temas penales?" | SERVICE_INFO | Info áreas legales |
| "¿Cuánto cobran?" | PAYMENT_INFO | Info honorarios |
| "Quiero agendar consulta" | BOOKING | Solicitar fecha/hora |
| "Estoy detenido" 🚨 | CASE_INQUIRY + URGENCY | Escalamiento urgente |

---

## ⏱️ TIMELINE ESTIMADO

| Fase | Tiempo | Dependencias |
|---|---|---|
| 1. Preparación Local | ✅ Ya hecho | - |
| 2. Migrar a GitHub | 15 min | Git configurado |
| 3. Servidor Ollama | 30-60 min | VPS o PC local |
| 4. Deploy Railway | 20 min | GitHub repo, Ollama listo |
| 5. Seed DB | 5 min | Railway desplegado |
| 6. Webhook WhatsApp | 10 min | Meta tokens |
| 7. Testing | 15 min | Todo anterior |
| **TOTAL** | **1.5-2 horas** | - |

---

## 💰 COSTOS ESTIMADOS

### Opción A: Servidor Local (Desarrollo)

| Servicio | Costo |
|---|---|
| Railway Pro | $20/mes |
| Electricidad (PC 24/7) | ~$25/mes |
| **TOTAL** | **~$45/mes** |

**Ventajas:**
- ✅ Económico
- ✅ Control total
- ✅ Sin límites de tokens

**Desventajas:**
- ❌ Depende de conexión local
- ❌ No 100% uptime

### Opción B: VPS con GPU (Producción)

| Servicio | Costo |
|---|---|
| Railway Pro | $20/mes |
| VPS GPU T4 (RunPod) | ~$216/mes |
| **TOTAL** | **~$236/mes** |

**Ventajas:**
- ✅ Alta disponibilidad
- ✅ Rendimiento consistente
- ✅ Escalable

**Desventajas:**
- ❌ Más costoso

---

## ⚠️ CONSIDERACIONES IMPORTANTES

### 1. Seguridad

- ✅ Cambiar `ADMIN_API_KEY` por valor complejo
- ✅ Usar `WHATSAPP_VERIFY_TOKEN` aleatorio fuerte
- ✅ No commitear archivos `.env` reales
- ✅ Configurar firewall en servidor Ollama
- ⚠️ Si usas IP pública en Ollama, considera VPN o autenticación adicional

### 2. Servidor Ollama

- GPU mínima recomendada: NVIDIA T4 (16 GB VRAM)
- Modelos ocupan:
  - `qwen2.5:7b`: ~4.7 GB
  - `llava:7b`: ~4.7 GB
  - **Total**: ~10 GB VRAM

### 3. Railway

- Plan Pro necesario para uptime continuo
- Límites Hobby: 500 horas/mes (~16 horas/día)
- PostgreSQL incluido sin cargo extra

### 4. WhatsApp Business

- Token expira cada 90 días (rotar)
- Límite mensajes: depende del tier de Meta
- Testing: usar número de prueba primero

---

## ✅ CHECKLIST FINAL

### Antes de Deploy

- [ ] Repositorio GitHub creado y pusheado
- [ ] README.md visible en GitHub
- [ ] Servidor Ollama funcionando (curl test OK)
- [ ] Tokens de WhatsApp obtenidos de Meta
- [ ] Cuenta Railway Pro activa

### Durante Deploy

- [ ] Proyecto Railway creado desde GitHub
- [ ] PostgreSQL agregado en Railway
- [ ] Variables de entorno configuradas
- [ ] Deploy exitoso (sin errores en logs)
- [ ] Health check responde: `/health`

### Post-Deploy

- [ ] Seed ejecutado (`seed_legal_rzj.py`)
- [ ] Webhook WhatsApp configurado
- [ ] Mensaje de prueba recibido y respondido
- [ ] Logs verificados (sin errores)
- [ ] Prueba de 5+ intenciones diferentes
- [ ] Prueba de urgencia ("estoy detenido")
- [ ] Documentar URL pública del bot

---

## 📞 SOPORTE Y TROUBLESHOOTING

### Railway Logs

```bash
# Ver logs en tiempo real
railway logs --follow

# Ver últimas 100 líneas
railway logs --lines 100
```

### Problemas Comunes

#### 1. "Connection refused to Ollama"

```bash
# Verificar Ollama está corriendo
curl http://TU_IP:11434/v1/models

# Ver logs del servidor Ollama
journalctl -u ollama -f
```

#### 2. "Database connection failed"

```bash
# Verificar DATABASE_URL
railway variables | grep DATABASE_URL

# Verificar PostgreSQL está running
railway status
```

#### 3. "Webhook verification failed"

- Verificar `WHATSAPP_VERIFY_TOKEN` coincide
- URL debe ser: `https://APP.railway.app/webhook/{PHONE_NUMBER_ID}`
- PHONE_NUMBER_ID debe ser el correcto de Meta

#### 4. "Bot no responde mensajes"

```bash
# Ver logs del webhook
railway logs --follow

# Verificar intent classifier
railway run python test_pipeline.py
```

---

## 📚 DOCUMENTACIÓN DE REFERENCIA

1. **`RAILWAY_DEPLOYMENT.md`** - Guía completa de deploy
2. **`PUSH_TO_GITHUB.md`** - Comandos Git exactos
3. **`RESUMEN_EJECUTIVO_RJZ.md`** - Vista ejecutiva
4. **`ANALISIS_ESTUDIO_JURIDICO.md`** - Diseño técnico
5. **`FLUJOS_CONVERSACIONALES_RJZ.md`** - Ejemplos de conversaciones

---

## 🎉 PRÓXIMOS PASOS POST-DEPLOY

Una vez todo funcione:

1. **Monitoreo**
   - Configurar alertas en Railway
   - Integrar Sentry para errores
   - Dashboard de métricas

2. **Optimización**
   - Agregar Redis para caching
   - Implementar rate limiting
   - Optimizar queries DB

3. **Features**
   - Integrar pagos (Stripe/MercadoPago)
   - Panel admin web (React)
   - Sistema de reportes

---

*Última actualización: Junio 2024*  
*Preparado para: Mediaciones RJZ*
