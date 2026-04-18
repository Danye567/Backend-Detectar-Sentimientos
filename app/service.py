from __future__ import annotations

import json
import os
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - se activa solo si la dependencia no está instalada.
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]

from .config import DEFAULT_MODEL, SYSTEM_PROMPT, MAX_HISTORY_MESSAGES
from .schemas import ChatMessage, SupportResponse


class TechnicalSupportBot:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL) -> None:
        effective_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=effective_key) if genai is not None and effective_key else None
        self.model = model

    def _build_system_instruction(self, user_name: str | None = None) -> str:
        instruction = SYSTEM_PROMPT
        if user_name:
            instruction += (
                f"\n\nEl nombre del usuario es {user_name}. "
                "Úsalo de forma natural cuando aporte valor."
            )
        return instruction

    def _build_contents(self, history: list[ChatMessage], user_message: str) -> list[Any]:
        contents: list[Any] = []
        for message in history[-MAX_HISTORY_MESSAGES:]:
            if message.role == "system":
                continue
            role = "model" if message.role == "assistant" else message.role
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=message.content)],
                )
            )
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=user_message)],
            )
        )
        return contents

    def _fallback_response(self, user_message: str) -> SupportResponse:
        lower = user_message.lower()
        if any(word in lower for word in ["pantalla", "no enciende", "apagado", "fuego", "humo", "golpe", "liquido"]):
            service = "Visita técnica"
        elif any(word in lower for word in ["limpieza", "mantenimiento", "actualizar", "backup", "respaldo", "optimizar"]):
            service = "Mantenimiento preventivo"
        else:
            service = "Asistencia remota"

        return SupportResponse(
            diagnosis="No fue posible consultar el modelo, así que te doy una orientación preliminar basada en el síntoma descrito.",
            possible_causes=[
                "Problema de configuración o software",
                "Falla de conexión o periféricos",
                "Requerimiento de revisión física si el equipo presenta daño visible",
            ],
            recommended_solution=(
                "Revisa el estado básico del equipo, reinícialo si es seguro hacerlo y valida "
                "si el problema se reproduce con otro cable, cargador o dispositivo."
            ),
            suggested_service=service,
            clarifying_questions=[
                "¿Qué mensaje de error o síntoma exacto aparece?",
                "¿Desde cuándo ocurre y qué cambió antes de que comenzara?",
            ],
        )

    def _normalize_response(self, data: dict[str, Any], user_message: str) -> SupportResponse:
        diagnosis = str(data.get("diagnosis", "")).strip() or "No se pudo generar un diagnóstico detallado."

        possible_causes_raw = data.get("possible_causes", [])
        if isinstance(possible_causes_raw, str):
            possible_causes = [possible_causes_raw.strip()] if possible_causes_raw.strip() else []
        else:
            possible_causes = [str(item).strip() for item in possible_causes_raw if str(item).strip()]

        recommended_solution = str(data.get("recommended_solution", "")).strip() or (
            "Verifica el comportamiento del equipo, reinícialo si es seguro y prueba con otro cable, "
            "cargador o periférico."
        )

        suggested_service_raw = str(data.get("suggested_service", "")).strip()
        service_map = {
            "asistencia remota": "Asistencia remota",
            "mantenimiento preventivo": "Mantenimiento preventivo",
            "visita técnica": "Visita técnica",
            "visita tecnica": "Visita técnica",
        }
        suggested_service = service_map.get(suggested_service_raw.lower(), "")
        if not suggested_service:
            suggested_service = self._fallback_response(user_message).suggested_service

        clarifying_questions_raw = data.get("clarifying_questions", [])
        if isinstance(clarifying_questions_raw, str):
            clarifying_questions = [clarifying_questions_raw.strip()] if clarifying_questions_raw.strip() else []
        else:
            clarifying_questions = [str(item).strip() for item in clarifying_questions_raw if str(item).strip()]

        return SupportResponse(
            diagnosis=diagnosis,
            possible_causes=possible_causes,
            recommended_solution=recommended_solution,
            suggested_service=suggested_service,
            clarifying_questions=clarifying_questions,
        )

    def chat(self, history: list[ChatMessage], user_message: str, user_name: str | None = None) -> tuple[SupportResponse, ChatMessage]:
        if self.client is None:
            support_response = self._fallback_response(user_message)
            assistant_message = ChatMessage(role="assistant", content=support_response.model_dump_json(ensure_ascii=False))
            return support_response, assistant_message

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=self._build_contents(history, user_message),
                config=types.GenerateContentConfig(
                    system_instruction=self._build_system_instruction(user_name),
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=SupportResponse,
                ),
            )
            if getattr(response, "parsed", None) is not None:
                parsed = response.parsed
                if isinstance(parsed, SupportResponse):
                    support_response = parsed
                else:
                    support_response = self._normalize_response(parsed.model_dump() if hasattr(parsed, "model_dump") else dict(parsed), user_message)
            else:
                content = getattr(response, "text", None) or "{}"
                data: dict[str, Any] = json.loads(content)
                support_response = self._normalize_response(data, user_message)
        except Exception:
            support_response = self._fallback_response(user_message)

        assistant_message = ChatMessage(role="assistant", content=support_response.model_dump_json(ensure_ascii=False))
        return support_response, assistant_message
