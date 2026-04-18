from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import DATA_DIR, JSON_HISTORY_PATH, SQLITE_PATH, MAX_HISTORY_MESSAGES
from .schemas import ChatMessage, ConversationState


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JsonConversationStore:
    def __init__(self, path: Path = JSON_HISTORY_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> dict[str, ConversationState]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

        sessions: dict[str, ConversationState] = {}
        for session_id, payload in raw.get("sessions", {}).items():
            messages = [
                ChatMessage(**message)
                for message in payload.get("messages", [])
                if message.get("role") in {"system", "user", "assistant"}
            ]
            sessions[session_id] = ConversationState(
                session_id=session_id,
                user_name=payload.get("user_name"),
                messages=messages[-MAX_HISTORY_MESSAGES:],
            )
        return sessions

    def save_all(self, sessions: dict[str, ConversationState]) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "updated_at": _utc_now(),
            "sessions": {
                session_id: {
                    "user_name": session.user_name,
                    "messages": [message.model_dump() for message in session.messages[-MAX_HISTORY_MESSAGES:]],
                }
                for session_id, session in sessions.items()
            },
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class SQLiteConversationStore:
    def __init__(self, db_path: Path = SQLITE_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_name TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_conversations_session_id
                ON conversations(session_id, id)
                """
            )

    def append_message(self, session_id: str, role: str, content: str, user_name: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO conversations (session_id, user_name, role, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, user_name, role, content, _utc_now()),
            )

    def load_messages(self, session_id: str) -> list[ChatMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content
                FROM conversations
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
        messages = [ChatMessage(role=row["role"], content=row["content"]) for row in rows]
        return messages[-MAX_HISTORY_MESSAGES:]

