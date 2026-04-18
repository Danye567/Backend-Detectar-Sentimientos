from __future__ import annotations

import argparse

from app.console import run_console


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot de soporte técnico")
    parser.add_argument("--api", action="store_true", help="Iniciar el backend REST con FastAPI")
    args = parser.parse_args()

    if args.api:
        import uvicorn

        uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
        return

    run_console()


if __name__ == "__main__":
    main()
