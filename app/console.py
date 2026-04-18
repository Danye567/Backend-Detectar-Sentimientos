from __future__ import annotations

from .config import DEFAULT_SESSION_ID
from .schemas import ChatMessage, ConversationState
from .service import TechnicalSupportBot
from .storage import JsonConversationStore, SQLiteConversationStore


def _render_response(response) -> None:
    print("\nDiagnóstico del problema:")
    print(response.diagnosis)
    print("\nPosibles causas:")
    for item in response.possible_causes:
        print(f"- {item}")
    print("\nSolución recomendada:")
    print(response.recommended_solution)
    print("\nTipo de servicio sugerido:")
    print(response.suggested_service)
    if response.clarifying_questions:
        print("\nPreguntas de aclaración:")
        for question in response.clarifying_questions:
            print(f"- {question}")
    print()


def run_console() -> None:
    json_store = JsonConversationStore()
    sqlite_store = SQLiteConversationStore()
    sessions = json_store.load_all()

    session_id = input(f"ID de sesión [{DEFAULT_SESSION_ID}]: ").strip() or DEFAULT_SESSION_ID
    user_name = input("Nombre del usuario (opcional): ").strip() or None

    session = sessions.get(session_id) or ConversationState(session_id=session_id, user_name=user_name, messages=[])
    if user_name:
        session.user_name = user_name

    bot = TechnicalSupportBot()

    print("\nChatbot de soporte técnico iniciado. Escribe 'salir' para terminar.\n")

    while True:
        user_input = input("Tú: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"salir", "exit", "quit"}:
            break
        if user_input.lower() == "/limpiar":
            session.messages = []
            sessions[session_id] = session
            json_store.save_all(sessions)
            print("Historial limpio.\n")
            continue

        response, assistant_message = bot.chat(session.messages, user_input, user_name=session.user_name)
        session.messages.append(ChatMessage(role="user", content=user_input))
        session.messages.append(assistant_message)
        session.messages = session.messages[-15:]

        sqlite_store.append_message(session_id, "user", user_input, user_name=session.user_name)
        sqlite_store.append_message(session_id, "assistant", assistant_message.content, user_name=session.user_name)

        _render_response(response)
        sessions[session_id] = session
        json_store.save_all(sessions)
