# Kavak Capital - Revisión de Conversaciones

Proyecto para consultar y revisar conversaciones de clientes desde BigQuery (Botmaker).

## Configuración

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar credenciales

Copia `.env.example` a `.env` y actualiza la ruta al archivo de credenciales:

```bash
cp .env.example .env
```

Edita `.env`:
```
GOOGLE_APPLICATION_CREDENTIALS=/Users/gabriellozano/Desktop/Kavak Capital Service Account.json
BQ_PROJECT=botmaker-bigdata
BQ_DATASET=ext_metric_kavakcapital
```

### 3. Verificar conexión

```bash
python test_connection.py
```

## Tablas disponibles

| Tabla | Descripción |
|-------|-------------|
| `message_metrics` | Mensajes individuales de cada conversación |
| `session_metrics` | Sesiones/conversaciones completas |

Proyecto BigQuery: `botmaker-bigdata`
Dataset: `ext_metric_kavakcapital`

## Uso básico

```python
from src.conversations import get_conversations_by_phone, get_sessions_by_phone

# Obtener mensajes de un lead
mensajes = get_conversations_by_phone(["+521234567890"])

# Obtener sesiones de múltiples leads
sesiones = get_sessions_by_phone(["+521234567890", "+529876543210"])
```
