# 🧪 GUÍA DE TESTING - BOT JURÍDICO MEDIACIONES RJZ

Esta guía explica cómo probar el sistema completo antes de ponerlo en producción.

---

## 📋 Pre-requisitos

### 1. Base de Datos Inicializada
```bash
# Asegurar que Docker esté corriendo
docker-compose up -d

# Ejecutar seed legal
python seed_legal_rzj.py
```

### 2. Completar PASO 5 (webhook.py)
- Ver instrucciones en `COMPLETAR_PASO_5_MANUAL.md`
- Reemplazar función `_route_intent` con versión legal

### 3. Dependencias Instaladas
```bash
pip install -r requirements.txt
```

---

## 🧪 SUITE DE TESTING AUTOMATIZADA

### Ejecutar Tests
```bash
python test_legal_bot.py
```

### ¿Qué prueba?
- ✅ Clasificación correcta de las 10 preguntas más frecuentes
- ✅ Extracción de entidades legales (legal_area, legal_matter, etc.)
- ✅ Detección de casos urgentes (is_detained → urgency=high)
- ✅ Generación de respuestas apropiadas
- ✅ Inclusión de disclaimers legales
- ✅ Escalamiento a abogado humano en casos críticos

### Resultado Esperado
```
================================================================================
📊 RESUMEN DE RESULTADOS
================================================================================

Total de pruebas: 10
✅ Pasadas: 10 (100.0%)
❌ Fallidas: 0 (0.0%)

================================================================================
🎉 ¡TODOS LOS TESTS PASARON! Sistema listo para producción.
================================================================================
```

---

## 🧪 TESTING MANUAL (Con WhatsApp Real)

### Paso 1: Configurar Tokens
```bash
# Actualizar en la base de datos o vía API
curl -X PATCH http://localhost:8000/admin/businesses/{BUSINESS_ID} \
  -H "X-Admin-Key: TU_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number_id": "TU_PHONE_NUMBER_ID_REAL",
    "whatsapp_token": "TU_TOKEN_REAL"
  }'
```

### Paso 2: Exponer con ngrok
```bash
# Iniciar el servidor
uvicorn app.main:app --reload

# En otra terminal, exponer con ngrok
ngrok http 8000
```

### Paso 3: Configurar Webhook en Meta
1. Ir a Meta for Developers → WhatsApp → Configuration
2. Configurar Webhook URL: `https://TU-NGROK-URL.ngrok-free.app/webhook/{PHONE_NUMBER_ID}`
3. Verify Token: (el que está en tu `.env`)
4. Suscribirse a eventos: `messages`

### Paso 4: Probar con WhatsApp
Enviar mensajes de prueba desde tu teléfono:

#### Test 1: Saludo
```
Mensaje: "Hola, quiero más información"
Esperado: Bienvenida de Mediaciones RJZ con áreas legales
```

#### Test 2: Consulta de Servicio
```
Mensaje: "¿Ven temas penales?"
Esperado: Lista de servicios de derecho penal
```

#### Test 3: Caso Específico
```
Mensaje: "Tengo un caso de tráfico de drogas"
Esperado: Confirmación de experiencia + CaseInquiry creado
```

#### Test 4: Honorarios
```
Mensaje: "¿Cuánto cobran?"
Esperado: Info de honorarios con rangos y formas de pago
```

#### Test 5: Plazos
```
Mensaje: "¿Cuánto demora un proceso de VIF?"
Esperado: Estimación de tiempo (2-4 meses) + disclaimer
```

#### Test 6: Agendamiento
```
Mensaje: "Quiero agendar una reunión"
Esperado: Solicitud de fecha y hora
```

#### Test 7: Identidad
```
Mensaje: "¿Con quién hablo?"
Esperado: Identificación como asistente virtual de Mediaciones RJZ
```

#### Test 8: Beneficios
```
Mensaje: "¿Puedo salir en libertad condicional?"
Esperado: Info general + invitación a consulta
```

#### Test 9: Antecedentes
```
Mensaje: "¿Qué pasa si tengo antecedentes previos?"
Esperado: Info sobre impacto + invitación a consulta
```

#### Test 10: 🚨 URGENTE (CRÍTICO)
```
Mensaje: "Estoy detenido, necesito ayuda urgente"
Esperado: 
  - Respuesta inmediata (< 30 segundos)
  - Mensaje: "Un abogado te contactará en 15-30 minutos"
  - CaseInquiry creado con urgency=high, is_detained=true
  - Notificación enviada al abogado
```

---

## ✅ CHECKLIST DE VALIDACIÓN

### Base de Datos
- [ ] Tablas `legal_categories`, `legal_services`, `case_inquiries` creadas
- [ ] Seed ejecutado: 3 categorías, 16 servicios
- [ ] Business con `business_type=LAW_FIRM`

### Intenciones
- [ ] 13 intenciones funcionando (6 mantenidas + 7 nuevas)
- [ ] Extracción de `legal_area`, `legal_matter` funciona
- [ ] Detección de `is_detained` funciona correctamente

### Respuestas
- [ ] Todas las respuestas incluyen disclaimers legales
- [ ] Tono profesional pero cercano
- [ ] Máximo 4-5 líneas por respuesta
- [ ] Emojis legales apropiados: ⚖️ 📋 👨‍⚖️

### Urgencias
- [ ] Palabra "detenido" → urgency=high automático
- [ ] CaseInquiry urgente crea notificación
- [ ] Respuesta de urgencia menciona 15-30 minutos
- [ ] HUMAN_SUPPORT se activa automáticamente

### Servicios
- [ ] `legal_services.py` funciona: búsqueda por área y asunto
- [ ] `case_inquiries.py` funciona: crear, actualizar, notificar
- [ ] `fee_info.py` funciona: formatear info de honorarios

### Webhook
- [ ] Función `_route_intent` actualizada con lógica legal
- [ ] Eliminadas referencias a products, orders, cart
- [ ] Todas las nuevas intenciones manejadas

---

## 🐛 TROUBLESHOOTING

### Error: "Module 'app.db.models' has no attribute 'LegalCategory'"
**Solución**: Ejecutar migraciones de base de datos
```bash
docker-compose down -v
docker-compose up -d
python seed_legal_rzj.py
```

### Error: "Intent 'CASE_INQUIRY' not found"
**Solución**: Verificar que `definitions.py` tiene las nuevas intenciones
```bash
grep "CASE_INQUIRY" app/intents/definitions.py
```

### Error: "Function '_route_intent' not handling CASE_INQUIRY"
**Solución**: Completar PASO 5 manualmente
- Ver `COMPLETAR_PASO_5_MANUAL.md`

### Respuestas sin disclaimers legales
**Solución**: Verificar `templates.py` tiene los prompts actualizados
```bash
grep "Esta es información general" app/prompts/templates.py
```

### Casos urgentes no notifican al abogado
**Solución**: Verificar `human_support_phone` en Business
```sql
SELECT name, human_support_phone FROM businesses;
```

---

## 📊 MÉTRICAS DE ÉXITO

### KPIs a Medir
| Métrica | Objetivo | Cómo Medir |
|---|---|---|
| Clasificación correcta | >80% | Test automatizado |
| Casos urgentes escalados | 100% | Revisar notificaciones |
| Tiempo de respuesta | <30 seg | Logs del sistema |
| Satisfacción del cliente | >4/5 | Encuesta post-consulta |
| Leads convertidos | >40% | Dashboard admin |

### Queries SQL para Métricas
```sql
-- Total de consultas recibidas
SELECT COUNT(*) FROM case_inquiries WHERE created_at >= NOW() - INTERVAL '7 days';

-- Casos urgentes
SELECT COUNT(*) FROM case_inquiries WHERE urgency = 'high' AND created_at >= NOW() - INTERVAL '7 days';

-- Tipo de caso más consultado
SELECT legal_matter, COUNT(*) as total
FROM case_inquiries
GROUP BY legal_matter
ORDER BY total DESC
LIMIT 10;

-- Tasa de conversión (leads → consultas agendadas)
SELECT 
  (SELECT COUNT(*) FROM bookings WHERE created_at >= NOW() - INTERVAL '7 days') * 100.0 /
  (SELECT COUNT(*) FROM leads WHERE created_at >= NOW() - INTERVAL '7 days') as conversion_rate;
```

---

## 🚀 CHECKLIST PRE-PRODUCCIÓN

### Técnico
- [ ] Todos los tests automatizados pasan (10/10)
- [ ] Tests manuales con WhatsApp reales completados
- [ ] Tokens de Meta actualizados (phone_number_id, whatsapp_token)
- [ ] Webhook configurado y verificado en Meta
- [ ] Base de datos con datos reales (no DEMO)
- [ ] Backups configurados
- [ ] Logs y monitoreo activos

### Funcional
- [ ] 10 preguntas frecuentes probadas manualmente
- [ ] Casos urgentes notifican correctamente
- [ ] Disclaimers legales en todas las respuestas
- [ ] Agendamiento de consultas funciona
- [ ] Presupuestos se generan correctamente
- [ ] Escalamiento a humano funciona

### Legal y Seguridad
- [ ] Disclaimers legales aprobados por abogado
- [ ] Privacidad de datos garantizada
- [ ] Cifrado de datos sensibles activo
- [ ] Cumplimiento GDPR / Ley 19.628 Chile
- [ ] Términos y condiciones actualizados

### Operacional
- [ ] Número del abogado configurado (`human_support_phone`)
- [ ] Horarios de atención actualizados
- [ ] Dirección de oficina correcta
- [ ] Formas de pago actualizadas
- [ ] Equipo capacitado en uso del sistema

---

## 📖 DOCUMENTACIÓN RELACIONADA

| Documento | Descripción |
|---|---|
| `RESUMEN_EJECUTIVO_RJZ.md` | Análisis completo y roadmap |
| `ESTADO_MIGRACION_LEGAL.md` | Estado de cada paso de migración |
| `COMPLETAR_PASO_5_MANUAL.md` | Instrucciones para webhook.py |
| `test_legal_bot.py` | Suite de testing automatizada |
| `seed_legal_rzj.py` | Seed con datos de RJZ |

---

## 📞 SOPORTE

¿Problemas o dudas? Consulta:
1. `ESTADO_MIGRACION_LEGAL.md` → Estado de los pasos
2. `TROUBLESHOOTING` (arriba) → Errores comunes
3. Logs del sistema: `docker-compose logs -f`

---

**✅ Sistema listo para producción cuando todos los checks estén completos**

*Última actualización: Junio 2024*
