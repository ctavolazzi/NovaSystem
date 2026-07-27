# Changelog

All notable changes to NovaSystem are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html),
with the caveat that NovaSystem is ALPHA software: minor versions may change
interfaces until 1.0.0.

## [Unreleased]

### Added

- **`novasystem.memory`**: queryable memory. The coworking Live Feed keeps
  events and the persona Ledger keeps decisions; both are good at recording and
  bad at being asked. This subpackage mirrors them into a PocketBase collection
  (`agent_journal`) you can search.
  - `novasystem journal status | log | query | recent | sync`
  - `journal.remember(...)` / `journal.recall(...)` from Python
  - `--all-projects` reads across every project sharing the collection, so
    NovaSystem can see what SimpleAgentOS learned and vice versa.
- Mirrors from `coworking.live_feed.LiveFeed.append` and
  `persona.ledger.Ledger.record`, both after their own write has committed.

Three properties this was built around:

- **Off by default.** Nothing mirrors unless `NOVA_JOURNAL=1`. Existing
  behavior is unchanged for anyone who doesn't opt in.
- **No import coupling.** SimpleAgentOS owns the PocketBase instance and the
  schema; NovaSystem speaks plain HTTP to the same collection and never imports
  it. Either project runs fine without the other.
- **Never fatal.** Every mirror is wrapped. A journal failure cannot fail a
  ledger `record()` or drop a feed row, and the ledger's hash chain is
  verified intact under a deliberately exploding journal in the tests.

Feed mirroring is filtered (`Write`, `Edit`, `NotebookEdit`, `note`, `focus`)
because mirroring every `Read` into a memory you later search buries the things
worth recalling. `NOVA_JOURNAL_FEED_KINDS=*` overrides.

### Fixed

- **The live tests were writing into the real journal.** `tests/memory/` pointed
  at the production `agent_journal` collection shared with SimpleAgentOS, so
  every run left `novatest-...` rows in a memory both projects read from. The
  `live` fixture now redirects `COLLECTION` to the scratch twin
  (`agent_journal_test`, owned by SimpleAgentOS's migrations) and deletes its
  rows on teardown. It skips with a clear message if that collection is absent.

- **The spool could grow without limit.** Capped at 8 MiB / 5000 entries /
  30 days via `NOVA_JOURNAL_SPOOL_MAX_*`, oldest dropped first, enforced on
  append behind a cheap `stat()`. The number of dropped entries is kept in a
  `.dropped` sidecar and reported by `novasystem journal status`, so memory lost
  to a long outage shows up as a known gap instead of a silent one.

## [0.2.0] - 2026-07-25

Two new subsystems. Both answer the same question from different directions:
when an AI agent works on your behalf, how do you know what it actually did?

The **coworking layer** answers it for humans, with a shared document you can
watch while the work happens. The **persona layer** answers it for machines,
with an append-only ledger of what an agent decided and why.

### Added: Coworking layer (`novasystem.coworking`)

A shared, human-readable workspace for working alongside an AI agent. One
markdown file per day, with the agent's current activity at the TOP where it
is visible without scrolling.

The organising insight is a layout decision, not a technical one. A log that
opens with yesterday's context and buries current activity 300 lines down is a
log nobody watches. Put the work where the eye already is and the document
becomes a live window rather than an archive.

**`config`**: every path and the section schema resolve here, so nothing else
hardcodes a location. Resolution order: explicit argument, then
`NOVA_COWORKING_DIR`, then a JSON config file, then defaults. Point it at an
Obsidian vault, a git repo, or any directory. Sections are data: define your
own in the config file and the migration, audit, and renderer all follow.

**`document`**: a markdown file with addressable sections and a safe write
API. Writes are atomic and lock-guarded so concurrent writers cannot lose each
other's work. Sections are permissioned: an agent cannot write sections the
schema reserves for you. Writes that change nothing raise rather than report
success, because a logging layer that silently drops writes is worse than none
at all, since you stop checking it.

**`live_feed`**: the section that makes the document watchable. A shell hook
appends one JSON line per agent tool call; this module rebuilds the whole
section from that log. The split is deliberate: recording is pure shell plus
`jq` and costs milliseconds, while a Python import costs roughly half a second,
which would be felt on every tool call. Rendering is a full rebuild rather than
an append, so double fires, races, and hand edits all converge on the same
correct content.

Consecutive runs of read-only tools collapse into one counted row: twelve
consecutive reads are one act of research, not twelve events worth of screen
space. The window holds fourteen rows and reports how many it trimmed. A
`Now:` headline carries intent, which tool calls never do. Rows are tagged by
session when more than one agent shares a feed.

**`migrate`**: schemas change; documents already on disk do not. This moves
whole sections to match the current schema. Content preserving: every section
body is compared before and after, and it refuses to write if anything
differs. Idempotent, verified by comparing rendered output rather than header
order. Dry run by default. Ad-hoc sections someone added by hand are kept, not
dropped.

**`audit`**: scans for what a session left behind: schema drift, headings
swallowed by a callout, a hook not installed or not executable, a feed running
ahead of the section that displays it, work done but never written down,
uncommitted trees. `--since HH:MM` scopes file checks to one session, because
several agents commonly share a repo and another session's dirty tree is not
your loose end.

**`install`**: installs the hook into Claude Code's settings. Backs the file
up first, preserves unrelated keys and hooks, is a no-op when run twice, and
aborts rather than overwriting a settings file that is not valid JSON.
Uninstall removes only what it added.

**CLI**: fourteen subcommands under `novasystem coworking`: `init`, `config`,
`status`, `render`, `show`, `read`, `write`, `focus`, `note`, `log`, `audit`,
`migrate`, `install-hook`, `uninstall-hook`, `doctor`.

**Tests**: 99 tests covering section splitting including headings inside code
fences, separator preservation, migration idempotence and content
preservation, feed collapsing and truncation, config precedence, and the
installer's handling of an existing settings file.

### Added: Persona layer (`novasystem.persona`)

Durable identity and decision history for Nova agents (DCE, CAE, domain
experts).

**`ledger`**: an append-only, hash-chained record of agent decisions. Each
entry links to its predecessor, so tampering with history breaks the chain
detectably rather than silently.

**`persona`**: versioned agent personas with `PersonaStore`, plus built-ins
for DCE, CAE, and domain experts.

**`precedent`**: recall of prior decisions that is checked by code rather
than self-reported by the model. An agent claiming consistency with past
decisions can be verified against the ledger instead of believed.

**`guardrail`**: a preservation interlock treating "do not destroy work" as a
guarantee separate from "do not corrupt work", with per-subtree verdicting via
`assess_tree_deletion`.

**`api`**: a FastAPI layer over the ledger, resolved lazily so the package
stays usable without FastAPI installed.

### Changed

- **`novasystem.cli` no longer imports `Nova` at module load.** It pulled in
  `docker` and `git` eagerly, so the CLI could not start on a machine without
  Docker. The coworking commands need neither. `Nova` is now constructed on
  demand, which means `novasystem coworking` works on a bare install.
- **`pyproject.toml` declares subpackages.** Only the top-level `novasystem`
  package was listed, so `persona`, `coworking`, `utils`, and `core_utils`
  were missing from a built wheel entirely.
- **Package data is declared.** The work log template and the agent hook are
  runtime assets. Without this they are absent from a wheel and
  `coworking init` fails on any install that is not an editable checkout.
- **Optional dependency groups.** `novasystem[coworking]` pulls `ruamel.yaml`
  and `portalocker`; `novasystem[persona-api]` pulls FastAPI and uvicorn;
  `novasystem[all]` pulls both. The base install stays lean and each layer's
  dependencies are visible rather than buried.

### Fixed

- **Replacing a section no longer eats the separator that follows it.** When a
  section's last line is a blockquote, which every callout-shaped section ends
  with, dropping the trailing `---` left the next `##` heading directly beneath
  a `>` line. Markdown lazy continuation then absorbed that heading into the
  callout and every section below it collapsed into one block. The separator is
  now preserved, and a section with no trailer gets a blank line so the next
  heading still escapes.
- **Appending to a section no longer nests the new entry inside the old one.**
  The mirror image of the same problem: a line following a blockquote without
  an intervening blank line is absorbed into that blockquote, so each entry
  nested one level deeper than the last and by the fifth the document was a
  staircase.
- **Layout migration strips every separator at a boundary, not just one.**
  Stripping one could not heal a document that already had `---\n\n---`: it
  removed a rule, the rejoin added one back, and the doubled rule survived
  every pass looking like a stable state.
- **Section fill state distinguishes template scaffolding from real content.**
  Determined by comparing against the rendered template rather than a list of
  known boilerplate strings, which drifts the moment someone edits the
  template.
- **`gitignore` no longer excludes the `novasystem` package** on
  case-insensitive filesystems.
- **`import novasystem` no longer requires Docker.** Public names resolve
  lazily via PEP 562.

### Notes

`novasystem.coworking` is derived from a working system that had been running
daily against a personal knowledge vault. Everything path-specific and
schema-specific was replaced with configuration during the port; the package
ships no reference to any personal workspace, and every test runs against a
temporary directory.

## [0.1.1] - 2026

### Added

- Automated repository installation: clone a repository, parse its
  documentation for installation commands, and execute them in an isolated
  Docker container.
- Command sequencing based on dependencies and priorities.
- Persistent storage of run data and execution results.
- CLI: `install`, `list-runs`, `show-run`, `delete-run`, `cleanup`.

## [0.1.0] - 2026

### Added

- Initial NovaSystem package: the Nova Process (UNPACK, ANALYZE, SYNTHESIZE)
  implemented over multiple cooperating agents.
