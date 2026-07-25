# Architecture: the coworking layer

**Status:** shipped in 0.2.0
**Package:** `novasystem.coworking`
**Audience:** anyone extending this layer or porting the idea elsewhere

This documents the decisions, including the ones that turned out to be wrong
the first time. The failure modes are the interesting part: each one is
cheap to reintroduce and expensive to diagnose.

---

## 1. What it is

A shared, human-readable workspace for working alongside an AI agent. One
markdown document per day, with named sections, written by several actors at
once: the agent in your terminal, a shell hook firing on every tool call, a
second agent session, and you in an editor.

The design constraint that shaped everything: **the document must stay
readable by a human at all times**, including mid-write, including while three
processes are appending to it. That rules out a database, rules out a binary
format, and makes markdown's quirks load-bearing rather than incidental.

## 2. Layout: work above context

The organising decision, and the only one that is really about product rather
than engineering.

Documents are conventionally written in narrative order: prior context, then
plan, then work. For a live document that is backwards. The top of a file is
the part visible without scrolling, which makes it the only part that gets
glanced at. Activity buried below the fold makes the document an archive.

So sections are grouped into two blocks and the work block goes first:

| Block | Sections | Read pattern |
|---|---|---|
| Work | Live Feed, Work, Decisions, Commits, Session Log | glanced at continuously |
| Context | Context, Research, Notes, Next, Links | read once, referred back to |

Consequence for contributors: **do not insert anything above the work block.**
The template marks the boundary with `<!-- /header -->`, and
`LiveFeed._ensure_section` anchors to it. Anything injected between the header
and the work block displaces exactly the content the layer exists to surface.

## 3. Module boundaries

```
config.py       paths + section schema        (no I/O, no dependencies)
   │
atomic.py       locking + atomic writes       (portalocker, optional)
frontmatter.py  YAML round-trip               (ruamel.yaml, lazy)
   │
document.py     sections, permissions, writes
   │
   ├── live_feed.py   activity feed → Live Feed section
   ├── migrate.py     schema changes → documents on disk
   └── audit.py       loose-end detection
          │
   install.py    agent-harness hook install
   cli.py        argparse surface
```

Rules that keep this honest:

- **`config` is the only module that knows a path.** Anything else hardcoding
  a location is a bug. This is what made the port from a personal system to a
  shippable package possible at all.
- **Nothing imports Docker or git.** The coworking layer runs on a machine
  with neither. `novasystem/cli.py` was changed in 0.2.0 to construct `Nova`
  lazily for this reason: it previously imported `docker` at module load, so
  the CLI could not start without it.
- **`install.py` is the only module that knows an agent harness exists.**
  Adding a second harness means adding to that file and nothing else.

## 4. Concurrency

Several writers, one file. The lock is advisory and lives at the workspace
root (`.coworking.lock`).

`portalocker` is an optional dependency, and its absence degrades to a
directory-mutex (`mkdir` is atomic everywhere worth supporting) rather than
failing. Losing cross-platform robustness is survivable; losing the ability to
write anything is not. A fallback lock older than the timeout is cleared, so
one crashed process cannot wedge the workspace for the rest of the day.

Writes go through `atomic_write`: temp file, fsync, `os.replace`. Readers see
the old file or the new one, never half of one. `DelayedKeyboardInterrupt`
wraps the critical section, because Ctrl+C landing between the temp write and
the rename is precisely how a truncated document happens.

## 5. Markdown lazy continuation: the two bugs

Both bugs in this section shipped and had to be fixed. They are the same
underlying rule seen from two directions, and both are invisible until a
document is already mangled.

**The rule.** In markdown, a line following a blockquote without an intervening
blank line is absorbed *into* that blockquote.

### 5a. Replacing a section ate its separator

`_replace_section` replaced everything between a header and the next header,
which includes the trailing `---`. For most sections that is merely untidy.
For a section whose last line is a blockquote (every callout-shaped section,
and the Live Feed always) the next `## Heading` landed directly beneath a `>`
line and was swallowed. Every section below it collapsed into one block.

Fixed by splitting the body into content and trailer, and re-emitting the
trailer:

```python
def _split_trailer(body):
    """The blank lines and `---` separating this section from the next.
    Layout, not content. Belongs to the document, not the writer."""
```

A section with no trailer at all still gets a blank line inserted, or the
heading is swallowed anyway.

### 5b. Appending nested each entry inside the last

The mirror image. Appending a new session-log entry directly onto the previous
one meant the new entry's first line followed a `>` line with no blank between
them, so it nested. By the fifth entry the document was a staircase.

Fixed in `_join_appended`, which inserts one blank unquoted line. The comment
there is deliberately emphatic; it is the kind of thing that gets "cleaned up"
by someone tidying whitespace.

**Guard:** `audit._check_structure` detects both, by looking for a `## ` line
whose predecessor starts with `>`.

## 6. Migration: content preservation over convenience

Schemas change. Documents on disk do not. `migrate` moves whole sections and
is built to fail loudly rather than half-apply:

1. Split into `(preamble, [(header, body), ...])`, fence-aware. A `## ` inside
   a code block is content, and a work log full of shell transcripts hits that
   immediately.
2. Compute target order: schema order first, unknown sections kept in relative
   order, tail sections pinned last. **Ad-hoc sections are never dropped.**
3. Reassemble with uniform separators.
4. Compare every `(header, normalized_body)` before and after. Any difference
   means refuse, not proceed.

**Idempotence is checked on rendered output, not header order.** A document can
be correctly ordered and still carry uneven spacing from an earlier pass; byte
equality is the only honest "nothing to do" signal.

The subtle one: `strip_trailing_rule` strips **every** trailing rule, not one.
Stripping a single rule cannot heal a document that already has `---\n\n---` at
a boundary. It removes one, the rejoin adds one back, and the doubled rule
survives every pass looking like a stable state.

## 7. The live feed: why it is split across two languages

```
tool call ─► PostToolUse hook ─► append JSONL      (bash + jq, ~10ms)
                    └──────────► detached render   (~500ms, off the hot path)
```

**Why shell records.** Importing this package costs roughly half a second.
Paying that on every `Read` is felt. The hook does the minimum, one `jq`
invocation and one append, and never blocks the tool call. It always exits 0;
an observability layer does not get to fail the thing it observes.

**Why the hook captures raw values.** All formatting lives in `live_feed.py`,
so changing how a row renders never means editing shell.

**Why render is a full rebuild.** Appends compound their own mistakes. A
regenerate-from-source render makes double fires, cross-session races, and
hand edits all converge on the same correct content. It also sidesteps 5a
entirely, since there is no incremental state to corrupt.

**Coalescing.** A `mkdir` lock allows one render in flight; a 0.4s sleep lets a
burst of tool calls land in one rebuild. A `Stop` hook renders synchronously at
end of turn, so the last coalesced-away render is never lost.

**Noise control.** Consecutive runs of read-only tools collapse to one counted
row. Runs from different sessions never merge, because two agents reading in
parallel are not one act of research. The window is capped and reports its
trim, since silent truncation reads as "that was everything".

## 8. Permissions

Sections carry a `writable` flag. Automated actors (`agent`, `hook`, `cron`,
and friends) are refused on sections marked otherwise; a human actor is not.

This is a product decision expressed as an API: an agent that can silently
rewrite your own notes is a worse collaborator, not a more capable one.

## 9. Failing loudly

Two places deliberately raise where a quieter design would not:

- **`SilentNoOp`.** A write that changed nothing raises rather than reporting
  success. A logging layer that silently drops writes is worse than none,
  because you stop checking it and it stays wrong.
- **Malformed config and malformed agent settings.** Both abort. Silently
  ignoring a config someone wrote is a debugging trap, and overwriting a
  settings file that failed to parse loses whatever else was in it.

The audit inverts this for its own checks: a check that raises is reported as a
finding and the run continues, because an audit that dies partway has told you
less than one that finishes.

## 10. Provenance and the port

This layer is derived from a system that had been running daily against a
personal knowledge vault. The port to a shippable package was mostly one kind
of work: every hardcoded path became configuration, and every schema assumption
became data.

Verification that it is genuinely portable is mechanical rather than trusted:
the package contains no reference to any personal workspace, defaults resolve
under `~/.novasystem`, and every test runs against a temporary directory.

## 11. Extending it

**A new harness.** Add entries to `install.py`. Nothing else knows harnesses
exist. The hook payload parser (`LiveFeed.record_payload`) is already tolerant
of shape, because harnesses disagree about `tool_name` vs `tool`.

**A new section type.** Add it to the schema in config or a user's JSON. The
migration adds it to existing documents on the next run.

**A new audit check.** Add a method to `Auditor` and list it in `checks()`.
Return `(status, [details])`. Assume it may raise.

**A different document format.** `document.py` is the only module that parses
markdown structure. `migrate.py` has its own fence-aware splitter because it
operates on text with no live `Document`. Those two are the porting surface.

---

**See also**
[Practical guide](../guides/ai-coworking.md) ·
[System overview](01-system-overview.md) ·
[CHANGELOG](../../CHANGELOG.md)
