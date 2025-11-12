from __future__ import annotations

import hashlib
import uuid


def generate_id(prefix: str = "ent", length: int = 12) -> str:
    """Generate a readable, prefixed unique ID.

    Uses UUID4 hex truncated to `length` for compactness.
    Examples: "ent_1a2b3c4d5e6f"
    """
    if length <= 0:
        length = 12
    return f"{prefix}_{uuid.uuid4().hex[:length]}"


def short_hash(data: str, length: int = 8) -> str:
    """Deterministic short hash for strings (hex, truncated)."""
    if not isinstance(data, (bytes, bytearray)):
        data = str(data).encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    return digest[:max(1, length)]
