# Backend Chatbot de Soporte Técnico con Gemini

Chatbot de soporte técnico en Python con:

- Historial de conversación con roles `system`, `user` y `assistant`
- Persistencia en JSON
- Persistencia opcional en SQLite
- Interacción continua por consola
- API REST con FastAPI para integración futura
- Respuestas estructuradas en:
  - Diagnóstico del problema
  - Posibles causas
  - Solución recomendada
  - Tipo de servicio sugerido

## Variables de entorno

- `GEMINI_API_KEY`: clave de Gemini
- `GEMINI_MODEL`: opcional, por defecto `gemini-2.5-flash`
- `CHATBOT_SESSION_ID`: opcional, por defecto `default`
- `CHATBOT_USER_NAME`: opcional, nombre para personalizar la conversación

Puedes crear un archivo `.env` en la raíz a partir de `.env.example`:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
CHATBOT_SESSION_ID=default
CHATBOT_USER_NAME=TuNombre


## Ejecución por consola

```bash
python main.py
```

## API REST

```bash
uvicorn app.api:app --reload
```

## Estructura

- `app/` contiene la lógica principal del chatbot
- `data/` se crea automáticamente para guardar el historial JSON y la base SQLite
