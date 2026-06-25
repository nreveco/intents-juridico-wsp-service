# ⚠️ COMPLETAR PASO 5 MANUALMENTE

## Estado Actual:
- ✅ **Imports actualizados** en webhook.py (eliminados products, orders, cart)
- ✅ **LegalCategory** reemplaza Category
- ✅ **Eliminados imports** de interactive buttons
- ✅ **Servicios legales creados** (legal_services.py, case_inquiries.py, fee_info.py)
- ⚠️ **FALTA:** Reemplazar función `_route_intent` completa

## Instrucciones Paso a Paso:

### 1. Abrir el archivo
```
d:\bot-jurico\wsp-engiener-intents-response-ia\app\routers\webhook.py
```

### 2. Buscar la línea 335 que dice:
```python
async def _route_intent(
```

### 3. Seleccionar y ELIMINAR desde esa línea hasta el FINAL del archivo
- La función `_route_intent` completa
- La función `_map_button_id` (si existe)

### 4. Copiar el contenido del archivo:
```
d:\bot-jurico\wsp-engiener-intents-response-ia\app\routers\webhook_legal_route.py
```

### 5. Pegar al final de webhook.py

### 6. Renombrar la función:
Cambiar `async def _route_intent_legal(` por `async def _route_intent(`

### 7. Guardar el archivo

## Verificación:

Ejecutar este comando para verificar que no hay errores de sintaxis:
```powershell
cd d:\bot-jurico\wsp-engiener-intents-response-ia
# Si tienes python instalado:
python -m py_compile app/routers/webhook.py
```

Si no muestra errores, el PASO 5 está completo.

## ✅ Una vez completado, continuar con PASO 6 (actualizar seed)
