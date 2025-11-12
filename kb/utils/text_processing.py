from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

import yaml


def extract_yaml_frontmatter(text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Extract YAML frontmatter from a Markdown document.

    Returns a tuple of (frontmatter_dict_or_None, body_text).
    Supports the common '---' ... '---' delimiters at the top of the file.
    If parsing fails or no frontmatter is present, returns (None, original_text).
    """
    if not text:
        return None, ""

    # Must start at beginning with optional BOM or whitespace then '---' on its own line
    # Capture everything until the next line that is exactly '---'
    # Use MULTILINE + DOTALL so '.' matches newlines and '^' anchors to line starts
    fm_pattern = re.compile(r"\A\ufeff?\s*---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

    match = fm_pattern.match(text)
    if not match:
        return None, text

    raw_yaml = match.group(1)
    body = text[match.end():]

    try:
        data = yaml.safe_load(raw_yaml) if raw_yaml.strip() else None
        if not isinstance(data, dict):
            # Normalize non-dict frontmatter to None to avoid surprises
            data = None
    except Exception:
        # On YAML parse errors, treat as no frontmatter and keep original text
        return None, text

    return data, body


def _strip_code_blocks(md: str) -> str:
    # Remove fenced code blocks ``` ``` and ~~~ ~~~
    md = re.sub(r"```[\s\S]*?```", " ", md)
    md = re.sub(r"~~~[\s\S]*?~~~", " ", md)
    return md


def _strip_inline_code(md: str) -> str:
    return re.sub(r"`[^`]*`", " ", md)


def _strip_links_and_images(md: str) -> str:
    # Replace markdown images entirely and keep the link label text for links
    md = re.sub(r"!\[[^\]]*\]\([^\)]*\)", " ", md)  # images -> drop
    md = re.sub(r"\[([^\]]*)\]\([^\)]*\)", r"\1", md)  # links -> keep label
    return md


def _strip_headings_md(md: str) -> str:
    # Remove heading markers only; keep the text
    return re.sub(r"^\s*#{1,6}\s+", "", md, flags=re.MULTILINE)


def calculate_word_count(text: str) -> int:
    """Approximate word count for Markdown content.

    - Removes YAML frontmatter
    - Strips code blocks, inline code, links/images, and heading markers
    - Counts words by whitespace separation
    """
    if not text:
        return 0

    _, body = extract_yaml_frontmatter(text)

    body = _strip_code_blocks(body)
    body = _strip_inline_code(body)
    body = _strip_links_and_images(body)
    body = _strip_headings_md(body)

    # Normalize whitespace
    body = re.sub(r"\s+", " ", body).strip()
    if not body:
        return 0

    return len(body.split(" "))
