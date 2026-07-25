"""Where the workspace lives and what sections a document has.

Everything path-shaped and schema-shaped is resolved here so no other module
hardcodes a location. Resolution order, highest priority first:

    1. an explicit argument passed to ``load_config()``
    2. environment variables (``NOVA_COWORKING_DIR``, ``NOVA_COWORKING_CONFIG``)
    3. a JSON config file (``~/.novasystem/coworking.json`` by default)
    4. the defaults in this module

The defaults are deliberately boring: ``~/.novasystem/coworking``. Point it
somewhere you already read, which is the whole point:

    export NOVA_COWORKING_DIR=~/Vault/Daily

JSON rather than YAML or TOML for the config file, on purpose. It is stdlib on
every supported Python, so a broken config is a parse error with a line number
rather than a missing dependency.

## Layout

The section order is the load-bearing design decision in this package.

The work block comes FIRST, directly under the document header, because the
top of a document is what a person sees without scrolling. A log that opens
with yesterday's context and buries current activity 300 lines down is a log
nobody watches. Put the work where the eye already is and the document becomes
a live window instead of an archive.

The context block follows: material you read once and refer back to.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ENV_DIR = "NOVA_COWORKING_DIR"
ENV_CONFIG = "NOVA_COWORKING_CONFIG"

DEFAULT_ROOT = Path.home() / ".novasystem" / "coworking"
DEFAULT_CONFIG_PATH = Path.home() / ".novasystem" / "coworking.json"

WORK = "work"
CONTEXT = "context"


@dataclass(frozen=True)
class Section:
    """One addressable section of a work log document."""

    name: str
    header: str
    block: str
    writable: bool = True
    placeholder: str = ""

    @property
    def title(self) -> str:
        return self.header.lstrip("# ").strip()


# The default schema. Work block on top; context block below.
#
# `writable` marks sections an automated actor may write. Sections left
# unwritable are the human's space: an agent that can rewrite your own notes
# is a worse collaborator, not a better one.
SECTION_SCHEMA: Tuple[Section, ...] = (
    Section(
        name="live_feed",
        header="## Live Feed",
        block=WORK,
        placeholder=("> [!abstract]+ Live Feed\n"
                     "> Idle. Rebuilt on every agent tool call.\n"),
    ),
    Section(name="work", header="## Work", block=WORK),
    Section(name="decisions", header="## Decisions", block=WORK),
    Section(name="commits", header="## Commits", block=WORK),
    Section(
        name="session_log",
        header="## Session Log",
        block=WORK,
        placeholder=("> [!info] Auto-generated\n"
                     "> One foldable entry per session.\n"),
    ),
    Section(name="context", header="## Context", block=CONTEXT),
    Section(name="research", header="## Research", block=CONTEXT),
    Section(name="notes", header="## Notes", block=CONTEXT, writable=False),
    Section(name="next", header="## Next", block=CONTEXT),
    Section(name="links", header="## Links", block=CONTEXT, writable=False),
)

# Sections pinned to the bottom during a layout migration, whatever else moves.
TAIL_SECTIONS: Tuple[str, ...] = ("## Links",)

# Marker delimiting the document header from the first section. Content is
# never inserted between this marker and the work block.
HEADER_END_MARKER = "<!-- /header -->"


@dataclass(frozen=True)
class Config:
    """Resolved paths and schema for one coworking workspace."""

    root: Path
    log_dir: Path
    feed_dir: Path
    template_path: Optional[Path] = None
    sections: Tuple[Section, ...] = SECTION_SCHEMA
    date_format: str = "%Y-%m-%d"
    source: str = "defaults"

    # ── Derived paths ──────────────────────────────────────────────────

    def log_path(self, date: Optional[str] = None) -> Path:
        """Path to one day's document."""
        return self.log_dir / f"{self._date(date)}.md"

    def feed_path(self, date: Optional[str] = None) -> Path:
        """Path to one day's raw activity log."""
        day = self._date(date)
        return self.feed_dir / day[:7] / f"{day}.jsonl"

    def state_path(self, date: Optional[str] = None) -> Path:
        """Sidecar holding the current focus headline."""
        day = self._date(date)
        return self.feed_dir / day[:7] / f"{day}.state.json"

    def lock_root(self) -> Path:
        """Directory whose lock file guards all writes in this workspace."""
        return self.root

    def _date(self, date: Optional[str]) -> str:
        if date:
            return date
        from datetime import datetime
        return datetime.now().strftime(self.date_format)

    # ── Schema access ──────────────────────────────────────────────────

    @property
    def headers(self) -> List[str]:
        """Section headers in document order."""
        return [s.header for s in self.sections]

    @property
    def by_name(self) -> Dict[str, Section]:
        return {s.name: s for s in self.sections}

    @property
    def by_header(self) -> Dict[str, Section]:
        return {s.header: s for s in self.sections}

    @property
    def writable(self) -> List[str]:
        return [s.name for s in self.sections if s.writable]

    def section(self, name: str) -> Section:
        try:
            return self.by_name[name]
        except KeyError:
            raise KeyError(
                f"unknown section {name!r}. Known: {', '.join(self.by_name)}"
            ) from None

    def with_root(self, root: Path) -> "Config":
        """Copy pointing at a different workspace root. Used by tests."""
        root = Path(root).expanduser()
        return replace(self, root=root, log_dir=root / "log",
                       feed_dir=root / "feed")


# ── Loading ────────────────────────────────────────────────────────────

def _sections_from_json(raw: Sequence) -> Tuple[Section, ...]:
    """Build a schema from config-file data.

    A partial entry inherits nothing: every section needs a name and a header,
    because a schema that silently half-applies is worse than one that refuses.
    """
    out = []
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise ValueError(f"sections[{i}] must be an object, got {type(entry).__name__}")
        missing = [k for k in ("name", "header") if not entry.get(k)]
        if missing:
            raise ValueError(f"sections[{i}] is missing: {', '.join(missing)}")
        header = str(entry["header"])
        if not header.startswith("#"):
            header = f"## {header}"
        out.append(Section(
            name=str(entry["name"]),
            header=header,
            block=str(entry.get("block", CONTEXT)),
            writable=bool(entry.get("writable", True)),
            placeholder=str(entry.get("placeholder", "")),
        ))
    if not out:
        raise ValueError("sections must not be empty")
    names = [s.name for s in out]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise ValueError(f"duplicate section names: {', '.join(sorted(dupes))}")
    return tuple(out)


def _read_config_file(path: Path) -> Dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"{path} is not valid JSON: {e}") from None
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def load_config(root: Optional[Path] = None,
                config_path: Optional[Path] = None) -> Config:
    """Resolve a Config from argument, environment, config file, then defaults.

    Never raises for a missing config file: absence means "use defaults", which
    is the common case. A config file that exists but is malformed DOES raise,
    because silently ignoring a config someone wrote is a debugging trap.
    """
    source = "defaults"
    data: Dict = {}

    cfg_path = (Path(config_path).expanduser() if config_path
                else Path(os.environ[ENV_CONFIG]).expanduser()
                if os.environ.get(ENV_CONFIG)
                else DEFAULT_CONFIG_PATH)
    if cfg_path.is_file():
        data = _read_config_file(cfg_path)
        source = str(cfg_path)

    resolved_root = None
    if root is not None:
        resolved_root, source = Path(root).expanduser(), "argument"
    elif os.environ.get(ENV_DIR):
        resolved_root = Path(os.environ[ENV_DIR]).expanduser()
        source = f"${ENV_DIR}"
    elif data.get("root"):
        resolved_root = Path(str(data["root"])).expanduser()
    else:
        resolved_root = DEFAULT_ROOT

    log_dir = (Path(str(data["log_dir"])).expanduser()
               if data.get("log_dir") else resolved_root / "log")
    feed_dir = (Path(str(data["feed_dir"])).expanduser()
                if data.get("feed_dir") else resolved_root / "feed")

    sections = (_sections_from_json(data["sections"])
                if data.get("sections") else SECTION_SCHEMA)

    template = (Path(str(data["template"])).expanduser()
                if data.get("template") else None)

    return Config(
        root=resolved_root,
        log_dir=log_dir,
        feed_dir=feed_dir,
        template_path=template,
        sections=sections,
        date_format=str(data.get("date_format", "%Y-%m-%d")),
        source=source,
    )


def default_template_path() -> Path:
    """Bundled template shipped with the package."""
    return Path(__file__).resolve().parent / "templates" / "worklog.md"


def describe(config: Config) -> str:
    """Human-readable summary, used by `novasystem coworking config`."""
    lines = [
        f"root        {config.root}",
        f"log dir     {config.log_dir}",
        f"feed dir    {config.feed_dir}",
        f"template    {config.template_path or default_template_path()}",
        f"resolved by {config.source}",
        "",
        "sections (document order):",
    ]
    for s in config.sections:
        flag = "rw" if s.writable else "r-"
        lines.append(f"  {flag}  {s.block:<7} {s.name:<12} {s.header}")
    return "\n".join(lines)
