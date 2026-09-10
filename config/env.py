import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


from typing import List, Optional


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in {"true", "1", "yes", "on"}


def get_env_list(key: str, default: str = "") -> List[str]:
    raw = os.getenv(key, default)
    values = []
    for item in raw.split(","):
        stripped_item = item.strip()
        if stripped_item:
            values.append(stripped_item)

    return values
