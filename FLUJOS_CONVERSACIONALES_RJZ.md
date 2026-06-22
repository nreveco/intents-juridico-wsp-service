# FLUJOS CONVERSACIONALES - MEDIACIONES RJZ
## Ejemplos Reales Basados en Preguntas Frecuentes

---

## 1. FLUJO: Cliente desde Instagram (Lead Capture)

### Escenario: Mensaje automático de Instagram
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"¡Hola! Quiero más información"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → GREETING + Lead Registration                  │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
¡Hola! Bienvenido a *Mediaciones RJZ* ⚖️

Somos un estudio jurídico especializado en:
• Derecho Penal (defensa, beneficios penitenciarios)
• Derecho de Familia (VIF, custodia, mediación)
• Derecho Civil (contratos, cobros, propiedades)

¿En qué materia legal podemos ayudarte hoy?
───────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│ 💾 BASE DE DATOS                                            │
└─────────────────────────────────────────────────────────────┘
✅ Lead creado:
   - phone: +56912345678
   - first_intent: "GREETING"
   - created_at: 2024-06-13 17:47:00
   - source: "Instagram"
```

---

## 2. FLUJO: "¿Ven temas penales?" (Service Info)

### Escenario: Cliente consulta especialidad
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"¿Ustedes ven temas penales?"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → SERVICE_INFO                                   │
│    IA Extrae: legal_area="penal"                            │
│    Consulta: LegalCategory WHERE name LIKE "%Penal%"        │
│    Consulta: LegalService WHERE category_id=penal           │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
Sí, nos especializamos en Derecho Penal ✅⚖️

Atendemos casos de:
• Ley 20.000 (tráfico y microtráfico de drogas)
• Violencia Intrafamiliar (VIF)
• Delitos contra las personas (homicidio, lesiones)
• Beneficios penitenciarios (libertad condicional)
• Apelaciones y recursos

¿Tienes un caso específico que consultar?

[📋 Ver servicios] [💬 Consultar mi caso] [📅 Agendar reunión]
───────────────────────────────────────────────────────────────
```

---

## 3. FLUJO: "¿Pueden hacer algo?" (Case Inquiry - CRÍTICO)

### Escenario: Cliente con caso de tráfico de drogas
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"Tengo un caso de tráfico de drogas, me pillaron con 384 gramos.
¿Pueden hacer algo? Tengo antecedentes cumplidos."

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → CASE_INQUIRY                                   │
│    IA Extrae:                                               │
│      - legal_matter: "tráfico de drogas"                    │
│      - urgency: "high"                                      │
│      - has_prior_record: True                               │
│      - description: "384 gramos, antecedentes cumplidos"    │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
Sí, podemos ayudarte con tu caso de Ley 20.000 ⚖️

Con 384g estás en tráfico (Art. 4° o 5°, no microtráfico).
Los antecedentes previos pueden agravar, pero hay estrategias
de defensa disponibles.

📋 Necesito saber:
• ¿Ya tuviste formalización? ¿Qué artículo te imputaron?
• ¿Estás con prisión preventiva o medidas cautelares?
• ¿Cuánto tiempo pasó desde los antecedentes cumplidos?

*Evaluación gratuita. Primera consulta sin costo.*

[📞 Llamar ahora] [📅 Agendar reunión] [💬 Seguir por chat]
───────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│ 💾 BASE DE DATOS                                            │
└─────────────────────────────────────────────────────────────┘
✅ CaseInquiry creado:
   - legal_matter: "Ley 20.000"
   - description: "384g, antecedentes cumplidos"
   - urgency: "high"
   - has_prior_record: True
   - status: "pending"

📲 NOTIFICACIÓN al abogado:
───────────────────────────────────────────────────────────────
⚠️ CONSULTA URGENTE - Ley 20.000
Cliente: +56912345678
Caso: Tráfico de drogas (384g)
Antecedentes: Sí (cumplidos)
[Ver detalles] [Responder]
───────────────────────────────────────────────────────────────
```

---

## 4. FLUJO: "¿Cuánto cobran?" (Payment Info)

### Escenario: Cliente pregunta por honorarios
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"¿Cómo son los pagos? ¿Cuánto cobran por un caso de VIF?"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → PAYMENT_INFO                                   │
│    IA Extrae: service_type="VIF"                            │
│    Consulta: FeeStructure WHERE service LIKE "%VIF%"        │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
Para casos de VIF, nuestros honorarios son 💰:

Base: $600.000 (puede variar según complejidad)

✅ Incluye:
• Representación en audiencias
• Coordinación de peritaje psicosocial
• Estrategia de defensa o acuerdos reparatorios
• Seguimiento completo del caso

💳 Formas de pago:
• 50% inicial, 50% al finalizar
• Facilidades de pago disponibles
• Primera consulta: GRATIS (evaluación del caso)

*Los honorarios finales se ajustan según complejidad.
Esta es una cotización referencial.*

¿Quieres que evaluemos tu caso específico?

[✅ Sí, evaluar] [📅 Agendar reunión] [❓ Más info]
───────────────────────────────────────────────────────────────
```

---

## 5. FLUJO: "¿Cuánto demora?" (Timeframe Query)

### Escenario: Cliente pregunta plazos
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"¿Cuánto tiempo se demora un proceso de VIF más o menos?"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → TIMEFRAME_QUERY                                │
│    IA Extrae: process_type="VIF"                            │
│    Consulta: CaseType.typical_timeframe WHERE name LIKE VIF │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
Los casos de VIF generalmente toman **2-4 meses** ⏱️

📋 Etapas típicas:
1️⃣ Denuncia y cautelares → 1-2 semanas
2️⃣ Investigación fiscal → 1-2 meses
3️⃣ Peritaje psicosocial → 2-4 semanas
4️⃣ Audiencia preparatoria → 1 mes
5️⃣ Juicio o acuerdo reparatorio → 2-4 semanas

⚠️ El plazo real depende de:
• Gravedad de los hechos
• Disponibilidad de peritos
• Complejidad del caso
• Tribunal donde se tramita

*Esta es información general. Para un cálculo preciso de
tu caso, agenda una consulta gratuita.*

[📅 Agendar ahora] [💬 Consultar mi caso]
───────────────────────────────────────────────────────────────
```

---

## 6. FLUJO: "¿Con quién hablo?" (Lawyer Identity)

### Escenario: Cliente quiere saber quién es
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"¿Con quién tengo el gusto? ¿Es un bot o una persona?"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → LAWYER_IDENTITY                                │
│    (Sin extracción, respuesta directa)                      │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
¡Hola! Soy el asistente virtual de *Mediaciones RJZ* 🤖⚖️

Estoy aquí para:
✅ Responder preguntas generales
✅ Agendar consultas
✅ Derivarte con nuestro abogado cuando lo necesites

Nuestro estudio está liderado por abogados especializados
en Derecho Penal, Familia y Civil.

Si tu caso requiere atención personalizada o es urgente,
puedo conectarte de inmediato con el abogado de turno.

¿Prefieres hablar directamente con un abogado?

[👨‍⚖️ Sí, hablar con abogado] [🤖 Seguir con asistente]
───────────────────────────────────────────────────────────────
```

---

## 7. FLUJO: Beneficios Penitenciarios

### Escenario: Cliente consultando libertad condicional
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"Tengo condena de 8 años por homicidio simple, llevo 5 años
y medio cumplidos. ¿Puedo pedir libertad condicional?"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → BENEFIT_INFO                                   │
│    IA Extrae:                                               │
│      - benefit_type: "libertad condicional"                 │
│      - sentence_total: "8 años"                             │
│      - time_served: "5.5 años"                              │
│      - crime: "homicidio simple"                            │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
✅ Sí, probablemente calificas para libertad condicional

📋 Requisitos Ley 18.216:
• Cumplir la mitad de la condena → Tú: 5.5/8 años ✅
• No tener sanciones disciplinarias graves
• Informe favorable de Gendarmería
• Certificado de arraigo (domicilio, trabajo/estudio)

⚠️ Para homicidio, el juez evalúa además:
• Conducta en el recinto penitenciario
• Actividades de reinserción (estudio, trabajo)
• Compromiso de no reincidencia

💰 Nuestro servicio:
• Tramitación completa: $450.000
• Evaluamos tus antecedentes penitenciarios
• Preparamos la solicitud
• Te representamos en audiencia

*Primera evaluación GRATIS. Te decimos si cumples requisitos.*

[✅ Evaluar mi caso] [📅 Agendar] [❓ Más info]
───────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│ 💾 BASE DE DATOS                                            │
└─────────────────────────────────────────────────────────────┘
✅ CaseInquiry creado:
   - legal_matter: "Beneficios penitenciarios - Libertad condicional"
   - description: "Homicidio simple, 8 años, cumplidos 5.5"
   - urgency: "medium"
   - status: "pending"
```

---

## 8. FLUJO: URGENCIA MÁXIMA - Cliente Detenido

### Escenario: Cliente en situación crítica ⚠️
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"Hola, me acaban de detener por tráfico de drogas. Tengo
audiencia de formalización mañana. Necesito abogado URGENTE."

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → CASE_INQUIRY                                   │
│    ⚠️ DETECCIÓN AUTOMÁTICA DE URGENCIA CRÍTICA             │
│    IA Extrae:                                               │
│      - legal_matter: "tráfico de drogas"                    │
│      - urgency: "high" (palabras: "detenido", "urgente")    │
│      - is_detained: True                                    │
│      - has_hearing_soon: True ("mañana")                    │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA INMEDIATA:
───────────────────────────────────────────────────────────────
🚨 ENTENDIDO - CASO URGENTE 🚨

Tu situación requiere atención INMEDIATA.
Un abogado de nuestro estudio te contactará en los próximos
**15 minutos** al número desde el que escribes.

📋 Mientras tanto:
• NO declares nada sin abogado presente
• NO firmes documentos sin revisarlos
• Anota nombre del fiscal y tribunal

Abogado de guardia: +56912345678
(Puedes llamar de inmediato si es posible)

⚖️ Atención 24/7 para casos urgentes
───────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│ 💾 BASE DE DATOS                                            │
└─────────────────────────────────────────────────────────────┘
✅ CaseInquiry creado:
   - urgency: "CRITICAL"
   - is_detained: True
   - has_hearing_soon: True
   - status: "urgent_pending"
   - priority: 1 (máxima)

┌─────────────────────────────────────────────────────────────┐
│ 🚨 NOTIFICACIONES AUTOMÁTICAS                               │
└─────────────────────────────────────────────────────────────┘

📲 WhatsApp al abogado:
───────────────────────────────────────────────────────────────
🚨 URGENCIA MÁXIMA 🚨
Cliente DETENIDO - Audiencia MAÑANA
Delito: Tráfico de drogas
Cliente: +56912345678
Estado: Necesita defensa inmediata
[VER CASO] [LLAMAR AHORA]
───────────────────────────────────────────────────────────────

📧 Email de alerta
📱 SMS de respaldo
🔔 Notificación push (si hay app móvil)

┌─────────────────────────────────────────────────────────────┐
│ 🔄 ESCALAMIENTO AUTOMÁTICO                                  │
└─────────────────────────────────────────────────────────────┘
✅ Conversación movida a HUMAN_HANDOFF
✅ Bot deja de responder (espera abogado)
✅ Timer iniciado: alerta si no hay respuesta en 15 min
```

---

## 9. FLUJO: Antecedentes Previos (Risk Assessment)

### Escenario: Cliente con historial penal
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"Yo tenía antecedentes cumplidos y prescrito, nunca declaré.
Ahora me pillaron de nuevo. ¿Qué riesgo corro? ¿Me pueden
mandar a la cárcel otra vez?"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → PRIOR_RECORD_QUERY                             │
│    IA Extrae:                                               │
│      - has_prior_record: True                               │
│      - record_status: "cumplido y prescrito"                │
│      - disclosed_records: False ("nunca declaré")           │
│      - urgency: "high" (reincidencia potencial)             │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
⚠️ Situación delicada - necesitas asesoría URGENTE

📋 Factores que agravan:
• Antecedentes previos aumentan pena (reincidencia)
• No haberlos declarado puede complicar defensa
• Riesgo de prisión preventiva es MAYOR

✅ Estrategias de defensa disponibles:
• Si el delito anterior prescribió legalmente, no debería
  considerarse como reincidencia
• Podemos argumentar que los antecedentes cumplidos no
  deben agravar la pena actual
• Negociación con fiscalía para reducir cargos

🚨 Necesitamos evaluar tu caso de inmediato:
• ¿Qué delito te imputan ahora?
• ¿Ya tuviste audiencia? ¿Estás con medidas cautelares?
• ¿Cuánto tiempo pasó desde los antecedentes cumplidos?

*Primera consulta GRATUITA - No esperes más*

[📞 Llamar ahora] [💬 Hablar con abogado] [📅 Agendar]
───────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│ 💾 BASE DE DATOS                                            │
└─────────────────────────────────────────────────────────────┘
✅ CaseInquiry creado:
   - has_prior_record: True
   - urgency: "high"
   - description: "Antecedentes cumplidos/prescritos, nueva detención"
   - requires_immediate_eval: True
```

---

## 10. FLUJO: Agendamiento de Consulta

### Escenario: Cliente quiere reunión presencial
```
┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"Quiero agendar una reunión para consultar mi caso"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → BOOKING                                        │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
📅 Perfecto, coordinemos tu consulta

Nuestros horarios:
• Lunes a viernes: 9:00 - 18:00
• Sábados: 10:00 - 14:00

Modalidad:
• Presencial (Av. Libertador Bernardo O'Higgins 1234, Of. 501)
• Videollamada (Google Meet / Zoom)

¿Qué día y hora te acomoda?
Ejemplo: "Mañana a las 15:00" o "Viernes 10:00 AM"
───────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│ 👤 CLIENTE                                                  │
└─────────────────────────────────────────────────────────────┘
"Mañana a las 15 horas presencial"

┌─────────────────────────────────────────────────────────────┐
│ 🤖 SISTEMA → Procesa Booking                                │
│    IA Extrae:                                               │
│      - datetime_requested: "mañana 15:00"                   │
│      - consultation_type: "presencial"                      │
└─────────────────────────────────────────────────────────────┘

📱 RESPUESTA:
───────────────────────────────────────────────────────────────
✅ Consulta agendada

📋 Resumen:
• Fecha: Jueves 14 de junio, 2024
• Hora: 15:00 hrs
• Modalidad: Presencial
• Lugar: Av. Libertador Bernardo O'Higgins 1234, Oficina 501
• Duración: 1 hora aprox.

📌 Trae contigo:
• Cédula de identidad
• Documentos relacionados al caso (si los tienes)
• Anotaciones o dudas específicas

⚠️ Primera consulta SIN COSTO

Te confirmaremos por WhatsApp 1 día antes.
¿Necesitas indicaciones de cómo llegar?

[📍 Ver mapa] [📞 Contactar] [✅ Confirmar]
───────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│ 💾 BASE DE DATOS                                            │
└─────────────────────────────────────────────────────────────┘
✅ InitialConsultation creado:
   - datetime_requested: "mañana 15:00"
   - datetime_confirmed: 2024-06-14 15:00:00
   - consultation_type: "presencial"
   - status: "CONFIRMED"
   - customer_phone: +56912345678

📲 Notificación al abogado:
───────────────────────────────────────────────────────────────
📅 Nueva consulta agendada
Cliente: +56912345678
Fecha: Jueves 14/06 - 15:00
Modalidad: Presencial
[Ver detalles] [Modificar agenda]
───────────────────────────────────────────────────────────────
```

---

## 📊 Matriz de Decisión: Cuándo Escalar a Humano

| Situación | Urgencia | Acción del Bot | Tiempo Escalamiento |
|---|---|---|---|
| Cliente detenido | 🔴 CRÍTICA | Respuesta + Escalar inmediato | <5 min |
| Audiencia hoy/mañana | 🔴 CRÍTICA | Respuesta + Escalar inmediato | <5 min |
| Cliente con caso complejo | 🟡 ALTA | Info general + ofrecer consulta | <30 min |
| Consulta de especialidad | 🟢 NORMAL | Responde con info + ofrecer agenda | Sin límite |
| Pregunta de honorarios | 🟢 NORMAL | Info general + disclaimer | Sin límite |
| Saludo inicial | 🟢 NORMAL | Bienvenida + captura lead | Sin límite |

---

*Documento de referencia para implementación de flujos conversacionales*  
*Basado en análisis de chat real de Mediaciones RJZ*  
*Versión: 1.0 - Junio 2024*
