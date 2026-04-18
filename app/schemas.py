from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


ServiceType = Literal["Asistencia remota", "Mantenimiento preventivo", "Visita técnica"]


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ConversationState(BaseModel):
    session_id: str
    user_name: Optional[str] = None
    messages: list[ChatMessage] = Field(default_factory=list)


class ChatRequest(BaseModel):
    session_id: str = "default"
    user_name: Optional[str] = None
    message: str


class SupportResponse(BaseModel):
    diagnosis: str
    possible_causes: list[str] = Field(default_factory=list)
    recommended_solution: str
    suggested_service: ServiceType
    clarifying_questions: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    session_id: str
    user_name: Optional[str] = None
    response: SupportResponse

