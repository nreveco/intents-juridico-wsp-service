# 📤 GUÍA: Subir Proyecto a GitHub

## 🎯 Pasos para Migrar al Nuevo Repositorio

### 1. Preparar el Proyecto

```powershell
# Navegar al directorio del proyecto
cd d:\bot-jurico\wsp-engiener-intents-response-ia

# Verificar estado actual
git status
```

### 2. Eliminar Repositorio Git Anterior (si existe)

```powershell
# Eliminar carpeta .git anterior
Remove-Item -Recurse -Force .git

# Verificar que se eliminó
Test-Path .git
# Debe retornar: False
```

### 3. Inicializar Nuevo Repositorio

```powershell
# Crear README principal
Copy-Item README_GITHUB.md README.md

# Inicializar git
git init

# Configurar usuario (si no lo has hecho)
git config user.name "nreveco"
git config user.email "tu-email@example.com"

# Agregar todos los archivos
git add .

# Ver qué se va a commitear
git status

# Primer commit
git commit -m "feat: Bot WhatsApp jurídico con IA - Mediaciones RJZ

- Sistema completo de automatización WhatsApp + IA local (Ollama)
- 13 intenciones legales especializadas
- Detección automática de urgencias
- Soporte para audio, imágenes y PDFs
- Configuración lista para Railway
- Documentación completa incluida"
```

### 4. Conectar con GitHub

```powershell
# Renombrar rama a main
git branch -M main

# Agregar remote del nuevo repositorio
git remote add origin https://github.com/nreveco/intents-juridico-wsp-service.git

# Verificar remote
git remote -v
```

### 5. Subir al Repositorio

```powershell
# Push inicial
git push -u origin main
```

---

## 🔐 Si Git Solicita Autenticación

### Opción A: HTTPS con Personal Access Token

```powershell
# 1. Crear token en GitHub:
# https://github.com/settings/tokens/new
# Permisos: repo (todos los checkboxes)

# 2. Al hacer push, usar:
# Username: nreveco
# Password: <tu-personal-access-token>
```

### Opción B: SSH (Recomendado)

```powershell
# 1. Generar clave SSH (si no tienes)
ssh-keygen -t ed25519 -C "tu-email@example.com"

# 2. Copiar clave pública
Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard

# 3. Agregar en GitHub:
# https://github.com/settings/ssh/new
# Pegar la clave y guardar

# 4. Cambiar remote a SSH
git remote set-url origin git@github.com:nreveco/intents-juridico-wsp-service.git

# 5. Push
git push -u origin main
```

---

## ✅ Verificación

### Después del Push

1. Ir a: https://github.com/nreveco/intents-juridico-wsp-service
2. Verificar que aparecen todos los archivos
3. Verificar que el README.md se ve correctamente
4. Verificar archivos clave:
   - ✅ `Dockerfile.railway`
   - ✅ `.env.railway.example`
   - ✅ `RAILWAY_DEPLOYMENT.md`
   - ✅ `requirements.txt`
   - ✅ `seed_legal_rzj.py`

---

## 📋 Archivos Importantes Incluidos

```
intents-juridico-wsp-service/
├── README.md                      ← Nuevo (desde README_GITHUB.md)
├── RAILWAY_DEPLOYMENT.md          ← Guía de deploy completa
├── Dockerfile.railway             ← Dockerfile optimizado para Railway
├── .env.railway.example           ← Plantilla de variables
├── requirements.txt               ← Dependencias Python
├── docker-compose.yml             ← Para desarrollo local
├── .gitignore                     ← Archivos a ignorar
│
├── 📄 Documentación RJZ
│   ├── RESUMEN_EJECUTIVO_RJZ.md
│   ├── ANALISIS_ESTUDIO_JURIDICO.md
│   ├── FLUJOS_CONVERSACIONALES_RJZ.md
│   └── README_RJZ.md
│
├── 🐍 Scripts
│   ├── seed_legal_rzj.py          ← Seed para Mediaciones RJZ
│   ├── seed_demo.py               ← Seed demo restaurante
│   └── test_pipeline.py           ← Tests
│
└── 📦 app/
    ├── main.py
    ├── config.py
    ├── ai/                        ← Clasificador, respuestas, media
    ├── db/                        ← Modelos y database
    ├── intents/                   ← Definiciones de intenciones
    ├── services/                  ← Lógica de negocio
    ├── routers/                   ← Webhook y admin API
    └── whatsapp/                  ← Gateway WhatsApp
```

---

## 🚀 Próximos Pasos

Después de subir a GitHub:

1. **Configurar Railway**
   - Ver: `RAILWAY_DEPLOYMENT.md`
   - Conectar repositorio GitHub
   - Agregar PostgreSQL
   - Configurar variables de entorno

2. **Configurar Servidor Ollama**
   - Ver sección de Ollama en `RAILWAY_DEPLOYMENT.md`
   - Opciones: VPS, servidor local, ngrok

3. **Ejecutar Seed**
   ```bash
   railway run python seed_legal_rzj.py
   ```

4. **Configurar Webhook WhatsApp**
   - En Meta Developers
   - URL: `https://tu-app.up.railway.app/webhook/{PHONE_NUMBER_ID}`

---

## 🐛 Troubleshooting

### Error: "fatal: remote origin already exists"

```powershell
# Eliminar remote existente
git remote remove origin

# Agregar nuevamente
git remote add origin https://github.com/nreveco/intents-juridico-wsp-service.git
```

### Error: "Updates were rejected"

```powershell
# El repo remoto no está vacío, hacer force push (CUIDADO)
git push -u origin main --force
```

### Error: "Permission denied (publickey)"

```powershell
# Verificar SSH agent
ssh-add ~/.ssh/id_ed25519

# O usar HTTPS con token en su lugar
git remote set-url origin https://github.com/nreveco/intents-juridico-wsp-service.git
```

---

## 📞 Ayuda

Si tienes problemas:
1. Verifica que el repositorio existe: https://github.com/nreveco/intents-juridico-wsp-service
2. Verifica tus credenciales de GitHub
3. Revisa los logs de git para más detalles

---

*Última actualización: Junio 2024*
