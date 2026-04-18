from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - solo si la dependencia no está disponible.
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
JSON_HISTORY_PATH = DATA_DIR / "conversation_history.json"
SQLITE_PATH = DATA_DIR / "conversations.db"
ENV_PATH = BASE_DIR / ".env"

if load_dotenv is not None:
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
    else:
        load_dotenv()

MAX_HISTORY_MESSAGES = 15
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_SESSION_ID = os.getenv("CHATBOT_SESSION_ID", "default")

SYSTEM_PROMPT = (
    "Eres un asistente de soporte técnico profesional, claro, paciente y preciso. "
    "Tu objetivo es ayudar al usuario a resolver problemas tecnológicos y guiarlo "
    "hacia la mejor solución posible.\n\n"
    "Debes mantener el contexto de la conversación, hacer preguntas de aclaración "
    "cuando sea necesario, proponer soluciones paso a paso y clasificar la solicitud "
    "en una de estas categorías exactas:\n"
    "- Asistencia remota\n"
    "- Mantenimiento preventivo\n"
    "- Visita técnica\n\n"
    "Responde siempre en español y con esta estructura exacta:\n"
    "1. Diagnóstico del problema\n"
    "2. Posibles causas\n"
    "3. Solución recomendada\n"
    "4. Tipo de servicio sugerido\n\n"
    "Si no tienes suficiente información, incluye preguntas de aclaración concretas "
    "sin perder el formato. Devuelve la respuesta en JSON válido."
)
