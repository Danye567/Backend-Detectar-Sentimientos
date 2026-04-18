from __future__ import annotations

from fastapi import FastAPI

from .schemas import ChatRequest, ChatResponse, ChatMessage, ConversationState
from .service import TechnicalSupportBot
from .storage import JsonConversationStore, SQLiteConversationStore


app = FastAPI(title="Soporte Técnico Chatbot", version="1.0.0")
json_store = JsonConversationStore()
sqlite_store = SQLiteConversationStore()
bot = TechnicalSupportBot()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    sessions = json_store.load_all()
    session = sessions.get(request.session_id) or ConversationState(
        session_id=request.session_id,
        user_name=request.user_name,
        messages=[],
    )
    if request.user_name:
        session.user_name = request.user_name

    response, assistant_message = bot.chat(session.messages, request.message, user_name=session.user_name)
    session.messages.append(ChatMessage(role="user", content=request.message))
    session.messages.append(assistant_message)
    session.messages = session.messages[-15:]

    sqlite_store.append_message(request.session_id, "user", request.message, user_name=session.user_name)
    sqlite_store.append_message(request.session_id, "assistant", assistant_message.content, user_name=session.user_name)

    sessions[request.session_id] = session
    json_store.save_all(sessions)

    return ChatResponse(session_id=request.session_id, user_name=session.user_name, response=response)
