# PASO 5 - INSTRUCCIONES PARA COMPLETAR

## ✅ Completado hasta ahora:
1. ✅ Actualizados los imports en webhook.py
2. ✅ Cambiado Category por LegalCategory
3. ✅ Creado archivo `webhook_legal_route.py` con la función `_route_intent_legal()` completa

## 🔧 Falta completar en `app/routers/webhook.py`:

### Opción 1: Reemplazo Manual (Recomendado)
1. Abrir `app/routers/webhook.py` en el editor
2. Localizar la función `async def _route_intent(...)` (línea ~330)
3. **Eliminar toda la función _route_intent** desde su definición hasta el final (incluyendo la función `_map_button_id`)
4. **Copiar** el contenido del archivo `webhook_legal_route.py` y pegarlo al final de webhook.py

### Opción 2: Eliminar referencias a interactive buttons
Si prefieres mantener el archivo actual y solo eliminar las referencias obsoletas:

1. **Eliminar estos imports** (líneas ~20-25):
```python
from app.whatsapp.interactive import (
    send_catalog_list,
    send_order_confirmation_buttons,
    send_welcome_buttons,
)
```

2. **Reemplazar la función `_route_intent`** completa (desde línea ~330 hasta ~530)
   - Copiar desde `webhook_legal_route.py` la función `_route_intent_legal`
   - Renombrarla a `_route_intent` (quitar el sufijo "_legal")
   - Pegarla en webhook.py reemplazando la función antigua

3. **Eliminar la función `_map_button_id`** (al final del archivo, después de _route_intent)

---

## 📋 Verificación Post-Cambios

Después de realizar los cambios, verificar:

### ✅ Imports correctos:
```python
from app.db.models import (
    Business,
    BusinessSettings,
    LegalCategory,  # ✅ Cambiado de Category
    Conversation,
    ConversationStatus,
    Message,
)
from app.intents.definitions import Intent
from app.services import bookings, handoff, leads, notifications, quotes
from app.services import legal_services, case_inquiries, fee_info  # ✅ Nuevos servicios
```

### ❌ NO deben aparecer estos imports:
```python
from app.services import cart, orders, products  # ❌ ELIMINAR
```

### ✅ La función `_route_intent` debe manejar estas intenciones:
- Intent.GREETING
- Intent.BOOKING
- Intent.QUOTE_REQUEST
- Intent.HOURS_QUERY
- Intent.LOCATION_QUERY
- Intent.HUMAN_SUPPORT
- Intent.CASE_INQUIRY  ✅ NUEVO
- Intent.SERVICE_INFO  ✅ NUEVO
- Intent.PAYMENT_INFO  ✅ NUEVO
- Intent.TIMEFRAME_QUERY  ✅ NUEVO
- Intent.LAWYER_IDENTITY  ✅ NUEVO
- Intent.BENEFIT_INFO  ✅ NUEVO
- Intent.PRIOR_RECORD_QUERY  ✅ NUEVO

### ❌ NO deben aparecer estas intenciones:
- Intent.PRICE_QUERY  ❌
- Intent.PRODUCT_INFO  ❌
- Intent.ORDER_CREATE  ❌
- Intent.ORDER_STATUS  ❌
- Intent.CART_ADD  ❌
- Intent.CART_VIEW  ❌
- Intent.CART_CHECKOUT  ❌
- Intent.CART_CLEAR  ❌

---

## 🧪 Prueba Rápida

Después de los cambios, ejecutar:

```bash
cd d:\bot-jurico\wsp-engiener-intents-response-ia
python -c "from app.routers.webhook import router; print('✅ Webhook importado correctamente')"
```

Si no hay errores, el PASO 5 está completo.

---

## 📝 Resumen de Archivos Modificados en PASO 5:

| Archivo | Estado | Acción |
|---|---|---|
| `app/routers/webhook.py` | ⚠️ Parcial | Falta reemplazar `_route_intent` completa |
| `app/routers/webhook_legal_route.py` | ✅ Creado | Contiene la función legal lista |
| `app/services/legal_services.py` | ✅ Creado | PASO 4 |
| `app/services/case_inquiries.py` | ✅ Creado | PASO 4 |
| `app/services/fee_info.py` | ✅ Creado | PASO 4 |

---

## 🚀 Siguiente Paso

Una vez completado el PASO 5 manualmente:

**PASO 6: Actualizar el seed (`seed_legal_rzj.py`) con los nuevos modelos**

¿Necesitas ayuda para completar el PASO 5 manualmente o prefieres que continúe con el PASO 6?
