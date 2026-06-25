# 🚂 Railway Setup - Guía Rápida

## ✅ Checklist Pre-despliegue

- [ ] Tablas creadas en Railway usando `railway-init.sql`
- [ ] `DATABASE_URL` copiada de Railway a `.env` local
- [ ] Ollama corriendo en servidor externo (VPS o ngrok)
- [ ] Variables de entorno configuradas en Railway

---

## 1️⃣ Crear y Configurar Base de Datos

### En Railway Dashboard:

1. **New → PostgreSQL**
2. Espera 2-3 minutos a que se aprovisione
3. Click en el servicio PostgreSQL
4. Ve a **"Data"** o **"Query"** tab
5. Copia TODO el contenido de `railway-init.sql`
6. Pégalo en el editor y ejecuta
7. Verifica que se crearon las tablas:
   ```sql
   SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';
   -- Debería devolver: 13
   ```

### Copiar DATABASE_URL:

En Railway, ve a tu servicio PostgreSQL → **Variables**

Verás estas variables:
- `PGHOST` (ej: reseau.proxy.rlwy.net)
- `PGPORT` (ej: 13605)
- `PGUSER` (ej: postgres)
- `PGPASSWORD` (la contraseña)
- `PGDATABASE` (ej: railway)

**Opción A - Usar el script helper:**
```bash
python build_railway_url.py
# Te pedirá cada valor y construirá la URL automáticamente
# También puede verificar la conexión
```

**Opción B - Construir manualmente:**

La URL tiene este formato:
```
postgresql+asyncpg://USUARIO:PASSWORD@HOST:PUERTO/DATABASE
```

Ejemplo con tus datos:
```env
DATABASE_URL=postgresql+asyncpg://postgres:tu_password@reseau.proxy.rlwy.net:13605/railway
```

⚠️ **Importante:** Usa `postgresql+asyncpg://` (no `postgresql://`)

---

## 2️⃣ Verificar Conexión Local → Railway

```bash
# Test rápido
test.cmd -Quick

# Test completo de base de datos
test.cmd -Db

# Test de todo el sistema
test.cmd -System
```

**Salida esperada:**
```
✅ Conexión exitosa!
✅ Se encontraron 13 tablas
✅ Se encontraron 7 enums
✅ Se encontraron 1 negocios registrados
```

---

## 3️⃣ Configurar Ollama Externo

Railway no soporta modelos LLM pesados. Necesitas Ollama en otro lado:

### Opción A: ngrok (Rápido, para testing)

**En tu PC local:**
```bash
# 1. Asegúrate que Ollama esté corriendo
docker ps | findstr ollama

# 2. Expone el puerto 11434
ngrok http 11434

# 3. Copia la URL pública
# Ejemplo: https://abc123.ngrok.io
```

**En Railway:**
```env
OLLAMA_BASE_URL=https://abc123.ngrok.io/v1
```

⚠️ **Nota:** ngrok debe estar corriendo 24/7 para que funcione.

### Opción B: VPS (Producción)

**En tu VPS Ubuntu/Debian:**
```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Descargar modelos
ollama pull qwen2.5:7b
ollama pull llava:7b

# 3. Verificar
ollama list

# 4. Configurar Nginx (ver nginx.conf del proyecto)
# 5. Configurar SSL con Let's Encrypt
sudo certbot --nginx -d ollama.tudominio.com

# 6. Verificar
curl https://ollama.tudominio.com/api/tags
```

**En Railway:**
```env
OLLAMA_BASE_URL=https://ollama.tudominio.com/v1
```

---

## 4️⃣ Desplegar Aplicación en Railway

### Desde GitHub (Recomendado):

1. Push tu código a GitHub
2. En Railway: **New → GitHub Repo**
3. Selecciona tu repositorio
4. Railway detecta `Dockerfile` automáticamente
5. Espera el build (3-5 min)

### Desde Railway CLI:

```bash
# 1. Instalar CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Link al proyecto
railway link

# 4. Deploy
railway up
```

---

## 5️⃣ Configurar Variables de Entorno en Railway

En Railway, ve a tu servicio de la app → **Variables** → **Raw Editor**

Pega esto (reemplaza los valores):

```env
# Database (Railway lo provee automáticamente)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Ollama (tu servidor externo)
OLLAMA_BASE_URL=https://tu-ollama-url.com/v1
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_VISION_MODEL=llava:7b

# WhatsApp (desde Meta Developer Console)
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=tu_token_secreto_12345

# Admin API (genera una clave segura)
ADMIN_API_KEY=admin_key_super_secreta_123

# App
ENVIRONMENT=production
DEBUG=false
PORT=8000
```

Click **Save** → Railway redespliega automáticamente.

---

## 6️⃣ Verificar Despliegue

### Health Check:

```bash
curl https://tu-app.railway.app/health
```

**Respuesta esperada:**
```json
{"status": "healthy"}
```

### API Docs:

Abre en navegador:
```
https://tu-app.railway.app/docs
```

### Logs:

```bash
railway logs -f
```

Deberías ver:
```
Iniciando — creando tablas en base de datos...
Base de datos lista ✓
Application startup complete.
```

---

## 7️⃣ Configurar Webhook de WhatsApp

1. Ve a [Meta Developer Console](https://developers.facebook.com)
2. Tu app → **WhatsApp** → **Configuration**
3. Click **Edit** en Webhook
4. Configura:
   - **Callback URL**: `https://tu-app.railway.app/webhook`
   - **Verify Token**: El mismo de `WHATSAPP_VERIFY_TOKEN`
5. Click **Verify and Save**
6. Subscribe a: `messages`

---

## 8️⃣ Probar el Bot

Envía un WhatsApp a tu número configurado:

```
Hola
```

Deberías recibir el mensaje de bienvenida.

Prueba otras consultas:
```
¿Cuánto cuesta?
Quiero agendar una cita
¿Dónde están ubicados?
¿Qué servicios ofrecen?
```

---

## 🔍 Troubleshooting

### Error: "Cannot connect to database"

```bash
# Verifica DATABASE_URL
echo $DATABASE_URL

# Test local
python test_db_connection.py
```

### Error: "Ollama not responding"

```bash
# Verifica que Ollama esté accesible
curl https://tu-ollama-url/api/tags

# Verifica OLLAMA_BASE_URL en Railway
railway variables
```

### Error: "Webhook verification failed"

1. Verifica que `WHATSAPP_VERIFY_TOKEN` sea el mismo en Railway y Meta
2. Verifica que la URL del webhook sea correcta
3. Revisa logs: `railway logs -f`

### Error: "Table does not exist"

Ejecuta `railway-init.sql` de nuevo en Railway Console:

```bash
# En Railway → PostgreSQL → Data → Query
# Pega el contenido de railway-init.sql y ejecuta
```

---

## 📊 Monitoreo

### Recursos en Railway:

- CPU: ~200-500 MB RAM (sin carga)
- Database: ~50-100 MB (con datos demo)

### Logs importantes:

```bash
# Ver logs en tiempo real
railway logs -f

# Filtrar solo errores
railway logs -f | grep ERROR

# Ver últimas 100 líneas
railway logs --tail 100
```

### Métricas:

- Tiempo de respuesta: ~1-3s (depende de Ollama)
- Mensajes por segundo: ~10-20
- Uptime esperado: 99.9%

---

## 🎉 ¡Listo!

Si todo funcionó:
- ✅ Base de datos Railway conectada
- ✅ Tablas creadas
- ✅ App desplegada
- ✅ Ollama conectado
- ✅ Webhook configurado
- ✅ Bot respondiendo

**Siguiente paso:** Cargar tus propios datos de negocio usando los endpoints `/admin/*`

---

## 📚 Recursos

- [Railway Docs](https://docs.railway.app)
- [Meta WhatsApp API](https://developers.facebook.com/docs/whatsapp)
- [Ollama Docs](https://ollama.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)

---

¿Problemas? Revisa los logs: `railway logs -f`
