"""Move documents already on disk to the current section layout.

Schemas change. Reordering the template does nothing for the hundred documents
already written, and hand-editing a 30KB markdown file is how content gets
lost.

Guarantees, in the order they matter:

**Content preserving.** Section bodies are moved, never edited. Every
(header, body) pair is compared before and after, and the tool refuses to write
if anything differs. It would rather do nothing than half-migrate.

**Idempotent.** A second run is a no-op. This is checked by comparing rendered
output rather than header order, because a document can already be in the right
order and still carry uneven separator spacing from an earlier pass.

**Dry run by default.** Nothing is written without ``write=True``.

Ordering rule:

    1. Sections the schema knows appear in schema order.
    2. Sections the document has that the schema does not, meaning ad-hoc
       headings added by hand, keep their relative order and land after the
       schema sections. They are never dropped.
    3. Tail sections stay pinned at the bottom.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Sequence, Tuple

from . import atomic
from .config import TAIL_SECTIONS, Config, load_config
from .document import Document

SECTION_RE = re.compile(r'^##\s+\S')
FENCE_RE = re.compile(r'^\s*(```|~~~)')


# ── Parsing ────────────────────────────────────────────────────────────

def split_sections(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """Split a document into (preamble, [(header, body), ...]).

    Fence aware: a ``## `` line inside a code block is content, not a heading.
    A work log full of shell transcripts hits this immediately.
    """
    lines = text.splitlines(keepends=True)
    preamble: List[str] = []
    blocks: List[Tuple[str, str]] = []
    current_header: Optional[str] = None
    current_body: List[str] = []
    in_fence = False
    fence_marker = None

    in_frontmatter = text.startswith("---\n")
    frontmatter_closed = not in_frontmatter

    for i, line in enumerate(lines):
        # Frontmatter delimiters are neither headings nor fences.
        if not frontmatter_closed:
            preamble.append(line)
            if i > 0 and line.rstrip() == "---":
                frontmatter_closed = True
            continue

        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence, fence_marker = False, None

        if not in_fence and SECTION_RE.match(line):
            if current_header is not None:
                blocks.append((current_header, "".join(current_body)))
            current_header = line.rstrip("\n")
            current_body = []
            continue

        if current_header is None:
            preamble.append(line)
        else:
            current_body.append(line)

    if current_header is not None:
        blocks.append((current_header, "".join(current_body)))

    return "".join(preamble), blocks


def strip_leading_rule(text: str) -> str:
    """Drop blank lines and any standalone ``---`` rules from the front."""
    lines = text.splitlines()
    while lines:
        while lines and not lines[0].strip():
            lines.pop(0)
        if lines and lines[0].strip() == "---":
            lines.pop(0)
            continue
        break
    return "\n".join(lines)


def strip_trailing_rule(text: str) -> str:
    """Drop blank lines and any standalone ``---`` rules from the end.

    Strips ALL trailing rules, not one. A single-rule strip cannot heal a
    document that already has ``---\\n\\n---`` at a boundary: it removes one,
    the rejoin adds one back, and the doubled rule survives every pass looking
    like a stable state.
    """
    lines = text.splitlines()
    while lines:
        while lines and not lines[-1].strip():
            lines.pop()
        if lines and lines[-1].strip() == "---":
            lines.pop()
            continue
        break
    return "\n".join(lines)


def normalize_body(body: str) -> str:
    """Strip the separators bracketing a section body.

    Documents on disk are inconsistent about which side of a heading the rule
    sits on, so both ends are handled. A horizontal rule in the MIDDLE of a
    body is content and is left alone.
    """
    return strip_trailing_rule(strip_leading_rule(body))


# ── Ordering ───────────────────────────────────────────────────────────

def target_order(document_headers: Sequence[str],
                 schema_headers: Sequence[str]) -> List[str]:
    """Desired header sequence for one document."""
    tail_set = set(TAIL_SECTIONS)
    schema_body = [h for h in schema_headers if h not in tail_set]

    ordered = [h for h in schema_body if h in document_headers]
    extras = [h for h in document_headers
              if h not in schema_headers and h not in tail_set]
    tail = [h for h in TAIL_SECTIONS if h in document_headers]
    return ordered + extras + tail


def reassemble(preamble: str, blocks: Sequence[Tuple[str, str]],
               order: Sequence[str]) -> str:
    """Rebuild document text with sections in the given order."""
    by_header = {h: normalize_body(b) for h, b in blocks}
    parts = [strip_trailing_rule(preamble)]
    for header in order:
        body = by_header.get(header, "")
        parts.append(f"{header}\n\n{body}" if body else header)
    return "\n\n---\n\n".join(parts).rstrip("\n") + "\n"


# ── Migration ──────────────────────────────────────────────────────────

def migrate_document(date: Optional[str] = None, write: bool = False,
                     add_missing: bool = True,
                     config: Optional[Config] = None) -> Dict:
    """Reorder one document. Writes only when ``write=True``."""
    config = config or load_config()
    doc = Document(date, config)
    if not doc.exists():
        return {"status": "skipped", "reason": "no work log",
                "path": str(doc.path)}

    text = doc.read()
    preamble, blocks = split_sections(text)
    if not blocks:
        return {"status": "skipped", "reason": "no sections",
                "path": str(doc.path)}

    schema_headers = config.headers
    document_headers = [h for h, _ in blocks]

    # Add sections the schema gained since this document was written.
    added: List[str] = []
    if add_missing:
        for section in config.sections:
            if section.header not in document_headers:
                blocks = list(blocks) + [(section.header, section.placeholder)]
                document_headers.append(section.header)
                added.append(section.header)

    order = target_order(document_headers, schema_headers)
    new_text = reassemble(preamble, blocks, order)

    # Byte equality is the only honest "nothing to do" signal: a document can
    # be correctly ordered and still need its spacing evened out.
    if new_text == text:
        return {"status": "unchanged", "path": str(doc.path),
                "sections": len(blocks)}

    # Content preservation check. Every body must survive the move intact.
    _, new_blocks = split_sections(new_text)
    before = {h: normalize_body(b) for h, b in blocks}
    after = {h: normalize_body(b) for h, b in new_blocks}
    if before != after:
        return {
            "status": "refused",
            "reason": "content would change",
            "path": str(doc.path),
            "missing_or_extra": sorted(set(before) ^ set(after)),
            "modified": sorted(h for h in set(before) & set(after)
                               if before[h] != after[h]),
        }

    verb = "reorder" if (order != document_headers or added) else "tidy"
    result = {
        "status": f"would-{verb}" if not write
                  else {"reorder": "reordered", "tidy": "tidied"}[verb],
        "path": str(doc.path),
        "sections": len(blocks),
        "added": added,
        "before": document_headers,
        "after": list(order),
    }

    if write:
        atomic.write(doc.path, new_text, root=config.lock_root())

    return result


def migrate_all(write: bool = False,
                config: Optional[Config] = None) -> List[Dict]:
    """Migrate every document in the log directory, oldest first."""
    config = config or load_config()
    if not config.log_dir.is_dir():
        return []
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    dates = sorted(p.stem for p in config.log_dir.glob("*.md")
                   if pattern.match(p.stem))
    return [migrate_document(date, write=write, config=config)
            for date in dates]
