"""The work log document: a markdown file with addressable sections.

One plain markdown file per day. Any actor (the agent in your terminal, a shell
hook, a cron job, you in an editor) reads and writes named slots without
knowing the rest of the structure.

Sections are delimited by their ``##`` headers. Content between one header and
the next belongs to that section.

Three rules the whole design turns on:

**Writes are permissioned.** Sections are marked writable or not in the schema.
An agent that can silently rewrite your own notes is a worse collaborator, not
a more capable one.

**Writes never silently no-op.** ``write_section`` raises rather than report
success when it changed nothing. A logging layer that quietly drops writes is
worse than no logging layer, because you stop checking.

**Separators are layout, not content.** The ``---`` between sections belongs to
the document. Replacing a section preserves it, appending to one does not
disturb it. Both matter for the same reason, described at ``_split_trailer``.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from . import atomic, frontmatter
from .config import Config, Section, default_template_path, load_config

# Actors permitted to write sections flagged writable in the schema.
AUTOMATED_ACTORS = frozenset({"agent", "hook", "cron", "claude", "assistant"})


class SectionError(KeyError):
    """No such section in this document's schema."""


class PermissionDenied(PermissionError):
    """An automated actor tried to write a section reserved for the human."""


class SilentNoOp(RuntimeError):
    """A write produced no change and refused to report success."""


class Document:
    """One day's work log.

    >>> doc = Document()                     # today, default workspace
    >>> doc.create()                         # idempotent
    >>> doc.write_section("work", "- porting the coworking layer")
    >>> doc.read_section("work")
    """

    def __init__(self, date: Optional[str] = None,
                 config: Optional[Config] = None):
        self.config = config or load_config()
        self.date = date or datetime.now().strftime(self.config.date_format)
        self._tmpl_cache: Optional[Dict[str, str]] = None

    # ── Location ───────────────────────────────────────────────────────

    @property
    def path(self) -> Path:
        return self.config.log_path(self.date)

    def exists(self) -> bool:
        return self.path.is_file()

    def __repr__(self) -> str:
        return f"<Document {self.date} at {self.path}>"

    # ── Creation ───────────────────────────────────────────────────────

    def create(self, template_path: Optional[Path] = None) -> Path:
        """Create the document from a template. No-op if it already exists.

        Template tokens, all optional:

            {{date}}        2026-07-25
            {{date:FMT}}    strftime, e.g. {{date:%A, %B %d}}
            {{date-1}}      yesterday, same format rules: {{date-1:%Y-%m-%d}}
            {{date+1}}      tomorrow
            {{title}}       the document's human title

        Deliberately not Templater, Jinja, or any other engine: a work log
        template that needs a plugin installed is a work log you cannot create
        from a cron job at 6am.
        """
        if self.exists():
            return self.path

        tmpl = (Path(template_path) if template_path
                else self.config.template_path or default_template_path())
        if not tmpl.is_file():
            raise FileNotFoundError(f"template not found: {tmpl}")

        text = self.render_template(tmpl.read_text(encoding="utf-8"))

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with atomic.workspace_lock(self.config.lock_root()):
            if self.path.is_file():          # re-check under the lock
                return self.path
            atomic.atomic_write(self.path, text)
        return self.path

    def render_template(self, text: str) -> str:
        """Substitute date tokens in template text."""
        base = datetime.strptime(self.date, self.config.date_format)

        def _sub(match: "re.Match") -> str:
            offset = int(match.group(1) or 0)
            fmt = match.group(2) or self.config.date_format
            return (base + timedelta(days=offset)).strftime(fmt)

        text = re.sub(r'\{\{date([+-]\d+)?(?::([^}]+))?\}\}', _sub, text)
        return text.replace("{{title}}", self.title)

    @property
    def title(self) -> str:
        try:
            base = datetime.strptime(self.date, self.config.date_format)
        except ValueError:
            return self.date
        return base.strftime("%A, %B %d, %Y")

    # ── Reading ────────────────────────────────────────────────────────

    def read(self) -> str:
        """The whole document."""
        if not self.exists():
            raise FileNotFoundError(f"no work log at {self.path}")
        return self.path.read_text(encoding="utf-8")

    def read_section(self, name: str, raw: bool = False) -> str:
        """One section's body.

        The trailing ``---`` separator is layout rather than content, so it is
        stripped by default. Pass ``raw=True`` to see the bytes as stored.
        """
        section = self._section(name)
        body = _extract_section(self.read(), section.header)
        return body if raw else _split_trailer(body)[0]

    def read_all(self, raw: bool = False) -> Dict[str, str]:
        text = self.read()
        return {s.name: (_extract_section(text, s.header) if raw
                         else _split_trailer(_extract_section(text, s.header))[0])
                for s in self.config.sections}

    def status(self) -> Dict[str, str]:
        """Per-section fill state: absent, empty, template, or filled.

        The four states need four different responses, which is why they are
        not collapsed into a boolean. ``absent`` wants a migration, ``empty``
        and ``template`` want content, ``filled`` wants nothing.

        ``template`` is decided by comparing against the rendered template
        rather than a list of known boilerplate strings. Scaffolding like
        ``**Status:**`` is untouched template text, and a heuristic that tries
        to recognise stock phrasing gets it wrong the moment someone edits the
        template. Comparing to the actual source cannot drift.
        """
        text = self.read()
        shipped = self._template_bodies()
        out = {}
        for section in self.config.sections:
            if not _has_header(text, section.header):
                out[section.name] = "absent"
                continue
            body = _split_trailer(_extract_section(text, section.header))[0]
            normalized = body.strip()
            if not normalized:
                out[section.name] = "empty"
            elif normalized == shipped.get(section.header, "\0").strip():
                out[section.name] = "template"
            else:
                out[section.name] = "filled"
        return out

    def _template_bodies(self) -> Dict[str, str]:
        """Section bodies as the template ships them, rendered for this date."""
        if getattr(self, "_tmpl_cache", None) is not None:
            return self._tmpl_cache
        tmpl = self.config.template_path or default_template_path()
        bodies: Dict[str, str] = {}
        if tmpl.is_file():
            rendered = self.render_template(tmpl.read_text(encoding="utf-8"))
            for header in re.findall(r'^##\s+.+$', rendered, re.MULTILINE):
                bodies[header] = _split_trailer(
                    _extract_section(rendered, header))[0]
        self._tmpl_cache = bodies
        return bodies

    def headers(self) -> List[str]:
        """Section headers actually present, in document order."""
        return re.findall(r'^##\s+.+$', self.read(), re.MULTILINE)

    # ── Writing ────────────────────────────────────────────────────────

    def write_section(self, name: str, content: str, actor: str = "agent",
                      mode: str = "replace") -> Dict:
        """Write one section.

        ``mode="replace"`` overwrites the body. ``mode="append"`` adds a
        timestamped block after the existing one.

        Raises ``PermissionDenied`` if an automated actor targets a section the
        schema reserves, and ``SilentNoOp`` if the write changed nothing.
        """
        section = self._section(name)
        if actor in AUTOMATED_ACTORS and not section.writable:
            raise PermissionDenied(
                f"'{actor}' may not write '{name}'. Writable: "
                f"{', '.join(self.config.writable)}"
            )
        if mode not in ("replace", "append"):
            raise ValueError(f"mode must be 'replace' or 'append', got {mode!r}")

        text = self.read()
        stamp = datetime.now().strftime("%H:%M")

        if not _has_header(text, section.header):
            # Self-heal a document that predates this section rather than
            # dropping the write. Placement is the migration's job; getting the
            # content onto disk is this call's job.
            body = (f"**[{actor} @ {stamp}]**\n{content}"
                    if mode == "append" else content)
            new_text = (text.rstrip("\n")
                        + f"\n\n---\n\n{section.header}\n\n{body.rstrip()}\n")
            outcome = "section_created"
        elif mode == "append":
            old = _extract_section(text, section.header)
            merged = _join_appended(old, f"**[{actor} @ {stamp}]**\n{content}")
            new_text = _replace_section(text, section.header, merged)
            outcome = "appended"
        else:
            new_text = _replace_section(text, section.header, content)
            outcome = "replaced"

        if new_text == text and content.strip():
            existing, _ = _split_trailer(_extract_section(text, section.header))
            if existing.strip() != content.strip():
                raise SilentNoOp(
                    f"write to '{name}' produced no change; refusing to report "
                    f"success on a silent no-op"
                )

        atomic.write(self.path, new_text, root=self.config.lock_root())
        return {"status": outcome, "section": name, "actor": actor,
                "mode": mode, "timestamp": datetime.now().isoformat()}

    def append_session_log(self, focus: str, changes: Optional[List] = None,
                           next_steps: str = "", files: Optional[List] = None,
                           context: str = "", actor: str = "agent") -> Dict:
        """Append one foldable entry to the session log.

        Renders as nested callouts so a long day stays scannable:

            > [!note]- 18:27 - focus text
            > file · file
            >> [!info]- 3 changes
            >> - item
            > -> next step
        """
        stamp = datetime.now().strftime("%H:%M")
        changes = changes or []
        files = files or []

        lines = [f"> [!note]- {stamp} - {_oneline(focus)}"]
        if files:
            lines.append("> " + " · ".join(f"`{f}`" for f in files))
        if changes:
            label = "change" if len(changes) == 1 else "changes"
            lines.append(f">> [!info]- {len(changes)} {label}")
            lines += [f">> - {_oneline(c)}" for c in changes]
        if context:
            lines.append(">> [!tip]- Context")
            lines += [f">> {l}".rstrip() for l in context.strip().splitlines()]
        if next_steps:
            lines.append(f"> **->** {_oneline(next_steps)}")

        return self.write_section("session_log", "\n".join(lines) + "\n",
                                  actor=actor, mode="append")

    def update_frontmatter(self, fields: Dict) -> Dict:
        """Merge fields into frontmatter, preserving comments and key order."""
        text = self.read()
        new_text = frontmatter.update_fields(text, fields)
        atomic.write(self.path, new_text, root=self.config.lock_root())
        return {"status": "updated", "fields": list(fields)}

    def read_frontmatter(self) -> Dict:
        fm, _ = frontmatter.parse(self.read())
        return dict(fm) if fm else {}

    # ── Internals ──────────────────────────────────────────────────────

    def _section(self, name: str) -> Section:
        try:
            return self.config.section(name)
        except KeyError as e:
            raise SectionError(str(e)) from None


# ── Module-level text helpers ──────────────────────────────────────────
#
# Free functions rather than methods: the migration and audit modules operate
# on document text that may not correspond to a live Document instance.

def _has_header(text: str, header: str) -> bool:
    return bool(re.search(rf'^{re.escape(header)}\s*$', text, re.MULTILINE))


def _extract_section(text: str, header: str) -> str:
    """Body between a header and the next header of the same or higher level."""
    try:
        level = len(header) - len(header.lstrip("#"))
        pattern = (rf'^{re.escape(header)}\s*\n(.*?)'
                   rf'(?=^#{{1,{level}}} |\Z)')
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        return match.group(1) if match else ""
    except re.error:
        return ""


def _split_trailer(body: str):
    """Split a section body into (content, trailer).

    The trailer is the blank lines and ``---`` rule separating this section
    from the next. It is layout, not content, and it belongs to the document
    rather than to whoever writes the section.

    Getting this wrong has a specific, ugly failure: when a section's last line
    is a blockquote, which any callout-shaped section is, and the trailer is dropped,
    the next ``##`` heading lands directly beneath a ``>`` line. Markdown lazy
    continuation then absorbs that heading INTO the callout, and every section
    below it collapses into one block.
    """
    lines = body.splitlines(keepends=True)
    trailer: List[str] = []
    while lines:
        while lines and not lines[-1].strip():
            trailer.insert(0, lines.pop())
        if lines and lines[-1].strip() == "---":
            trailer.insert(0, lines.pop())
            continue
        break
    return "".join(lines), "".join(trailer)


def _replace_section(text: str, header: str, new_body: str) -> str:
    """Replace a section's body, preserving its trailing separator."""
    try:
        level = len(header) - len(header.lstrip("#"))
        pattern = (rf'(^{re.escape(header)}\s*\n)(.*?)'
                   rf'(?=^#{{1,{level}}} |\Z)')
        if not new_body.endswith("\n"):
            new_body += "\n"

        def _sub(match):
            _, trailer = _split_trailer(match.group(2))
            # No trailer at all still needs one blank line, or the next heading
            # is swallowed. See _split_trailer.
            if not trailer.startswith("\n"):
                trailer = "\n" + trailer
            return match.group(1) + new_body + trailer

        # A function replacement inserts new_body literally. A replacement
        # string would choke on backslashes, which real content contains.
        return re.sub(pattern, _sub, text, count=1,
                      flags=re.MULTILINE | re.DOTALL)
    except re.error:
        return text


def _join_appended(old_body: str, addition: str) -> str:
    """Join an appended block onto an existing body.

    The blank line between them is load-bearing, for the mirror image of the
    reason in ``_split_trailer``: a line following a blockquote without an
    intervening blank line is absorbed into that blockquote. Without this, each
    new entry nests inside the previous one instead of becoming its sibling,
    and by the fifth entry the document is a staircase.
    """
    addition = addition.rstrip("\n") + "\n"
    prefix = old_body.rstrip("\n")
    return f"{prefix}\n\n{addition}" if prefix else addition


def _oneline(value) -> str:
    """Collapse a value to one line.

    A stray newline in a commit subject would land unquoted inside a callout
    and break the reader out of the block: the same failure as a missing blank
    line, arriving from the other direction.
    """
    return " ".join(str(value).split())


