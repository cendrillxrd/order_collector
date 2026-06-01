import time
import uuid
from typing import Optional


def generate_uuid_id(prefix: Optional[str] = None) -> str:
    """
    Генерирует UUID-based ID
    """
    unique_id = str(uuid.uuid4())

    if prefix:
        return f"{prefix}-{unique_id}"
    return unique_id
