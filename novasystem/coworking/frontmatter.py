"""Round-trip YAML frontmatter for markdown documents.

Two problems with the obvious approach of handing the whole file to a YAML
parser:

1. Standard parsers strip comments, normalise flow-style sequences, reorder
   keys, and rewrite quote styles on every load/dump cycle. A document edited
   by an agent five times a day would be unrecognisable by evening.
2. Markdown bodies are full of lines that look like YAML. A ``---`` horizontal
   rule reads as a document separator; a ``- item`` list reads as a sequence.
   Feeding the body to the parser at all is the bug.

So: split the file at the frontmatter fence by hand, never let body text reach
the parser, and use ruamel's round-trip mode for the part that is genuinely
YAML.

``ruamel.yaml`` is imported lazily. Reading a document's sections does not
require it, and neither does ``import novasystem.coworking``.
"""

from __future__ import annotations

import io
from typing import Dict, Optional, Tuple

_MISSING_RUAMEL = (
    "ruamel.yaml is required to read or write document frontmatter.\n"
    "Install it with:  pip install 'novasystem[coworking]'   (or: pip install ruamel.yaml)"
)


def _yaml():
    """A YAML instance configured to preserve everything it can."""
    try:
        from ruamel.yaml import YAML
    except ImportError as e:  # pragma: no cover - depends on the install
        raise ImportError(_MISSING_RUAMEL) from e
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    y.width = 4096          # long wikilinks and URLs must not get line-wrapped
    y.allow_unicode = True
    return y


def _empty_map():
    try:
        from ruamel.yaml.comments import CommentedMap
    except ImportError as e:  # pragma: no cover
        raise ImportError(_MISSING_RUAMEL) from e
    return CommentedMap()


def split(text: str) -> Tuple[Optional[str], str]:
    """Split raw markdown into (frontmatter_text, body_text).

    Pure string work, no YAML parsing, so this is safe to call on any document
    and cheap enough to call often. Returns ``(None, text)`` when the document
    has no frontmatter block.

    A frontmatter block is recognised only when the file STARTS with a fence.
    The closing fence is the first ``---`` that sits alone on its own line.
    """
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text

    after_open = text[4:] if text.startswith("---\n") else text[5:]

    end_idx = -1
    search_from = 0
    while True:
        idx = after_open.find("\n---", search_from)
        if idx == -1:
            break
        tail = idx + 4
        if tail == len(after_open) or after_open[tail] in ("\n", "\r"):
            end_idx = idx
            break
        search_from = idx + 1

    if end_idx == -1:
        # Opening fence with no close: treat the whole file as body rather than
        # guessing where the author meant it to end.
        return None, text

    fm_text = after_open[:end_idx]
    body_start = end_idx + 4
    if body_start < len(after_open) and after_open[body_start] == "\n":
        body_start += 1
    return fm_text, after_open[body_start:]


def parse(text: str):
    """Split markdown into (frontmatter_map, body_text).

    The map is a ruamel ``CommentedMap`` so a later ``serialize`` round-trips
    comments and formatting. Returns ``(None, text)`` when there is no
    frontmatter.
    """
    fm_text, body = split(text)
    if fm_text is None:
        return None, body
    fm_map = _yaml().load(fm_text) if fm_text.strip() else _empty_map()
    if fm_map is None:
        fm_map = _empty_map()
    return fm_map, body


def serialize(fm, body: str) -> str:
    """Recombine a frontmatter map and a body into markdown."""
    if fm is None:
        return body
    buf = io.StringIO()
    _yaml().dump(fm, buf)
    fm_text = buf.getvalue().rstrip("\n") + "\n"
    return f"---\n{fm_text}---\n{body}"


def update_fields(text: str, fields: Dict) -> str:
    """Merge `fields` into the document's frontmatter and return new markdown.

    Existing keys, comments, anchors, and ordering survive. New keys are
    appended. A document with no frontmatter gets a block prepended.
    """
    fm, body = parse(text)
    if fm is None:
        fm = _empty_map()
        body = text
    for key, value in fields.items():
        fm[key] = value
    return serialize(fm, body)


def read_field(text: str, key: str, default=None):
    """Read one frontmatter value without requiring a full round-trip.

    Falls back to a minimal scanner when ruamel is unavailable, so read-only
    callers (the auditor, mostly) keep working on a bare install.
    """
    fm_text, _ = split(text)
    if fm_text is None:
        return default
    try:
        fm = _yaml().load(fm_text) or {}
        return fm.get(key, default)
    except ImportError:
        prefix = f"{key}:"
        for line in fm_text.splitlines():
            if line.startswith(prefix):
                return line[len(prefix):].strip() or default
        return default
