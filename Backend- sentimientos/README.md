# Backend de analisis de sentimientos

API en FastAPI que clasifica mensajes en `positivo`, `negativo` o `neutro`, detecta una intencion basica y devuelve una respuesta automatica con sugerencia de escalamiento a soporte tecnico cuando el mensaje es negativo.

## Objetivo del proyecto

Este proyecto busca demostrar:

- clasificacion basica de sentimiento
- deteccion simple de intencion
- separacion de capas en backend
- respuesta preparada para integrarse con un chatbot en el futuro

## Estructura

```text
main.py
routers/
  __init__.py
  analysis.py
schemas/
  __init__.py
  analysis.py
services/
  __init__.py
  analysis_service.py
  intent.py
  sentiment.py
  response_generator.py
requirements.txt
README.md
```

## Como ejecutar el proyecto

1. Abrir una terminal en la carpeta del proyecto.

2. Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

4. Iniciar el servidor:

```powershell
python -m uvicorn main:app --reload
```

5. Abrir la documentacion interactiva:

- `http://127.0.0.1:8000/docs`

## Que debe revisar el profesor

### 1. Endpoint principal

Probar `POST /analizar` en Swagger o con Postman.

Ejemplo de request:

```json
{
  "mensaje": "Tengo un problema con mi cuenta y no puedo entrar"
}
```

### 2. Respuesta esperada

El sistema debe devolver:

- `sentimiento`
- `intencion`
- `respuesta`
- `escalar_soporte`
- `contexto_chatbot`

Ejemplo de response:

```json
{
  "sentimiento": "negativo",
  "intencion": "queja",
  "respuesta": "Lamentamos la situacion que estas presentando. Vamos a ayudarte a revisar el problema con prioridad. Por favor, compartenos mas detalles para orientarte mejor. Recomendamos escalarlo a soporte tecnico para continuar con la atencion.",
  "escalar_soporte": true,
  "contexto_chatbot": {
    "canal_recomendado": "escalar_a_soporte",
    "requiere_agente_humano": true,
    "siguiente_accion": "crear_ticket_y_derivar_a_soporte",
    "resumen": "sentimiento=negativo; intencion=queja; escalar_soporte=True"
  }
}
```

### 3. Casos de prueba recomendados

- Mensaje positivo:
  - `Gracias por darme la ayuda que necesito`
- Mensaje negativo:
  - `Tengo un problema, el sistema no funciona y da error`
- Mensaje neutro:
  - `Necesito informacion sobre el estado de mi solicitud`

## Flujo de funcionamiento

1. El usuario envia un mensaje al endpoint `POST /analizar`.
2. FastAPI valida el cuerpo de la solicitud.
3. El backend detecta sentimiento e intencion.
4. Si el sentimiento es negativo, marca `escalar_soporte = true`.
5. El sistema genera una respuesta automatica.
6. Se devuelve un JSON listo para integrarse con un chatbot.

## Buenas practicas incluidas

- separacion de responsabilidades por capas
- `schemas` para entrada y salida tipada
- `services` para la logica de negocio
- `routers` para la capa HTTP
- validacion con Pydantic
- manejo centralizado de errores
- respuesta pensada para futura integracion con chatbot

## Nota para la evaluacion

Si el profesor quiere comprobar el funcionamiento, basta con:

1. iniciar el servidor
2. entrar a `/docs`
3. ejecutar `POST /analizar`
4. verificar que:
   - un mensaje negativo sugiera soporte tecnico
   - un mensaje positivo sea clasificado correctamente
   - la respuesta incluya el contexto para chatbot

