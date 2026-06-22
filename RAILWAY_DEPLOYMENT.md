# 🚂 GUÍA DE DESPLIEGUE EN RAILWAY

## 📋 Prerrequisitos

- [x] Cuenta en Railway.app
- [x] Repositorio en GitHub
- [x] Token de WhatsApp Business de Meta
- [x] API Key de OpenAI (o servidor Ollama externo)

---

## 🎯 Arquitectura: Railway + Ollama Externo

Railway no soporta GPU, por lo que necesitas un **servidor externo con Ollama** para ejecutar los modelos de IA.

### Opciones para Servidor Ollama:

**Opción 1: VPS con GPU (Recomendado)**
- Providers: Paperspace, RunPod, Lambda Labs, Vast.ai
- Costo: ~$0.30-0.50/hora GPU (~$200-350/mes)
- Ventaja: Control total, sin límite de tokens

**Opción 2: Servidor Local (Tu PC/Servidor)**
- Exponer Ollama con Cloudflare Tunnel o ngrok
- Costo: $0 (solo electricidad)
- Ventaja: Gratis
- Desventaja: Disponibilidad depende de tu conexión

**Opción 3: Railway + Ollama en Modo CPU (No Recomendado)**
- Muy lento sin GPU
- Solo para pruebas

---

## 🚀 PASO A PASO: Despliegue en Railway

### 1. Preparar el Repositorio GitHub

```bash
cd d:\bot-jurico\wsp-engiener-intents-response-ia

# Crear nuevo README para el repo público
git checkout -b main
git add .
git commit -m "Preparar para Railway deployment"

# Conectar con el nuevo repositorio
git remote remove origin  # Si existe
git remote add origin https://github.com/nreveco/intents-juridico-wsp-service.git
git push -u origin main
```

### 2. Crear Proyecto en Railway

1. Ir a [railway.app](https://railway.app)
2. Click en **"New Project"**
3. Seleccionar **"Deploy from GitHub repo"**
4. Autorizar acceso a GitHub
5. Seleccionar: `nreveco/intents-juridico-wsp-service`

### 3. Agregar PostgreSQL

1. En el proyecto de Railway, click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway creará automáticamente la base de datos
3. La variable `DATABASE_URL` se inyecta automáticamente

### 4. Configurar Variables de Entorno

En Railway → **Variables**, agregar:

```env
# Ollama (servidor externo)
OLLAMA_BASE_URL=http://TU_IP_PUBLICA:11434/v1
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_VISION_MODEL=llava:7b

# WhatsApp Meta Cloud API
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=mi_token_super_secreto

# Admin
ADMIN_API_KEY=admin_key_super_secreta_cambiar

# App
ENVIRONMENT=production
DEBUG=false
```

**NOTA:** `DATABASE_URL` y `PORT` son inyectadas automáticamente por Railway.

### 5. Desplegar

1. Railway detectará el `Dockerfile.railway` automáticamente
2. Click en **"Deploy"**
3. Esperar 3-5 minutos para el build
4. Obtener la URL pública: `https://tu-app.up.railway.app`

### 6. Ejecutar Seed de Base de Datos

```bash
# Opción A: Desde local (conectando a Railway DB)
# Copiar DATABASE_URL desde Railway
export DATABASE_URL="postgresql://postgres:xxxxx@xxxxx.railway.app:5432/railway"
python seed_legal_rzj.py

# Opción B: Usando Railway CLI
railway run python seed_legal_rzj.py
```

### 7. Configurar Webhook de WhatsApp

1. Ir a [developers.facebook.com](https://developers.facebook.com)
2. Tu App → WhatsApp → Configuration → Webhook
3. **Callback URL:** `https://tu-app.up.railway.app/webhook/{PHONE_NUMBER_ID}`
4. **Verify Token:** El mismo de `WHATSAPP_VERIFY_TOKEN`
5. Suscribirse a: `messages`
6. Click **"Verify and Save"**

---

## 🎯 CONFIGURACIÓN DE SERVIDOR OLLAMA EXTERNO

Necesitas un servidor con GPU para Ollama. Aquí las opciones:

### Opción A: VPS con GPU (RunPod, Paperspace, etc.)

```bash
# 1. Crear instancia con GPU (ej: NVIDIA T4 o RTX 4090)
# 2. SSH al servidor
ssh user@tu-servidor-ip

# 3. Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 4. Configurar Ollama para aceptar conexiones externas
export OLLAMA_HOST=0.0.0.0:11434

# 5. Iniciar Ollama como servicio
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

# 6. Descargar modelos
ollama pull qwen2.5:7b
ollama pull llava:7b

# 7. Configurar firewall (permitir puerto 11434)
sudo ufw allow 11434/tcp

# 8. Verificar que funciona
curl http://localhost:11434/v1/models
```

**Obtener IP Pública:**
```bash
curl ifconfig.me
# Usar esta IP en Railway: http://IP_PUBLICA:11434/v1
```

### Opción B: Servidor Local con Cloudflare Tunnel (Gratis)

```bash
# 1. En tu PC con Ollama instalado
ollama serve

# 2. Instalar Cloudflare Tunnel
# Windows: descargar desde https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
# Linux/Mac:
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# 3. Autenticar
cloudflared tunnel login

# 4. Crear túnel
cloudflared tunnel create ollama-bot

# 5. Configurar túnel
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: <TUNNEL_ID_QUE_OBTUVISTE>
credentials-file: /home/USER/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: ollama.tudominio.com
    service: http://localhost:11434
  - service: http_status:404
EOF

# 6. Ejecutar túnel
cloudflared tunnel run ollama-bot

# Ahora puedes usar: https://ollama.tudominio.com/v1
```

### Opción C: ngrok (Temporal, para pruebas)

```bash
# 1. Instalar ngrok: https://ngrok.com/download
# 2. En terminal separada con Ollama corriendo:
ngrok http 11434

# 3. Copiar URL pública (ej: https://abc123.ngrok-free.app)
# 4. Usar en Railway: https://abc123.ngrok-free.app/v1
```

---

## 🎯 OPCIÓN 2: Servidor Ollama Externo

Si tienes un servidor con GPU (AWS, GCP, servidor propio):

### Setup del Servidor Ollama

```bash


## 📊 Estimación de Costos

### Railway
- **Hobby Plan:** $5/mes (500 horas)
- **Pro Plan:** $20/mes (ilimitado)
- **PostgreSQL:** Incluido

### Servidor Ollama con GPU
**VPS GPU (RunPod, Paperspace):**
- GPU T4: ~$0.30/hora = ~$216/mes
- GPU RTX 4090: ~$0.50/hora = ~$360/mes

**Servidor Local:**
- $0/mes (solo electricidad ~$20-30/mes)

### Total Estimado
**Con VPS GPU:**
- Railway Pro: $20/mes
- VPS GPU: $216-360/mes
- **TOTAL:** ~$236-380/mes

**Con Servidor Local:**
- Railway Pro: $20/mes
- Electricidad: ~$25/mes
- **TOTAL:** ~$45/mes

---

## ✅ Checklist de Despliegue

- [ ] Repositorio en GitHub creado
- [ ] Proyecto Railway creado
- [ ] PostgreSQL agregado en Railway
- [ ] Variables de entorno configuradas
- [ ] Deploy exitoso (sin errores)
- [ ] Seed ejecutado (`seed_legal_rzj.py`)
- [ ] Webhook de WhatsApp configurado
- [ ] Prueba de mensaje: "Hola" → Respuesta del bot
- [ ] Verificar logs: `railway logs`
- [ ] Probar intenciones: consulta legal, agendamiento, etc.

---

## 🔍 Monitoreo y Logs

```bash
# Ver logs en tiempo real
railway logs --follow

# Ver servicios
railway status

# Conectar a PostgreSQL
railway connect postgres
```

---

## 🐛 Troubleshooting

### Error: "Connection refused to database"
```bash
# Verificar que DATABASE_URL está configurada
railway variables

# Reiniciar el servicio
railway restart
```

### Error: "OpenAI API key not found"
```bash
# Verificar variable OPENAI_API_KEY
railway variables
```

### Webhook no recibe mensajes
1. Verificar URL: `https://tu-app.up.railway.app/webhook/{PHONE_NUMBER_ID}`
2. Verificar `WHATSAPP_VERIFY_TOKEN` coincide
3. Ver logs: `railway logs`

---

## 📈 Optimizaciones Futuras

1. **Rate Limiting:** Agregar Redis para limitar requests
2. **Caching:** Cachear respuestas frecuentes
3. **Queue System:** Bull/BullMQ para mensajes en cola
4. **Monitoring:** Sentry para errores, Prometheus para métricas
5. **CDN:** Cloudflare para assets estáticos

---

## 🔒 Seguridad

- [ ] Cambiar `ADMIN_API_KEY` por valor seguro
- [ ] Usar `WHATSAPP_VERIFY_TOKEN` complejo
- [ ] Habilitar HTTPS (Railway lo hace automáticamente)
- [ ] Rotar tokens cada 90 días
- [ ] Limitar acceso a admin endpoints por IP

---

## 📞 Soporte

- **Railway:** https://railway.app/help
- **Meta WhatsApp:** https://developers.facebook.com/support
- **OpenAI:** https://help.openai.com

---

*Última actualización: Junio 2024*
