import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)

_PLACEHOLDER_VALUES = frozenset({
    "your_openai_api_key",
    "your_gemini_api_key",
    "your_groq_api_key",
})

def _env_value(name: str) -> str | None:
    value = os.getenv(name)
    if not value or value.strip() in _PLACEHOLDER_VALUES:
        return None
    return value.strip()

def get_gemini_api_key() -> str | None:
    return _env_value("GEMINI_API_KEY") or _env_value("GOOGLE_API_KEY")

MODEL_REGISTRY = {
    "gpt-4o": {
        "provider": "openai", 
        "display_name": "OpenAI GPT-4o",
        "base_url": None
    },
    "gemini-2.5-flash": {
        "provider": "google", 
        "display_name": "Google Gemini 2.5 Flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/"
    },
    "llama-3.3-70b-versatile": {
        "provider": "groq",
        "display_name": "Groq Llama 3.3 70B Versatile",
        "base_url": "https://api.groq.com/openai/v1"
    }
}

def validate_environment():
    checks = [
        ("OPENAI_API_KEY", "OpenAI", _env_value("OPENAI_API_KEY")),
        ("GEMINI_API_KEY", "Gemini", get_gemini_api_key()),
        ("GROQ_API_KEY", "Groq", _env_value("GROQ_API_KEY")),
    ]

    missing = [name for name, _, value in checks if not value]

    if missing:
        for name in missing:
            provider = next(label for key, label, _ in checks if key == name)
            logging.error(
                f"Missing or placeholder API key: {name} ({provider}). "
                f"Copy .env.example to .env in {_PROJECT_ROOT} and set real keys."
            )
        sys.exit(1)