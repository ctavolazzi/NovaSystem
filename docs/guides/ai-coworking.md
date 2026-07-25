# AI Coworking: a practical guide

**Audience:** anyone who works with a coding agent and cannot tell what it did.
**Time to working setup:** about five minutes.
**Requires:** NovaSystem 0.2.0+, `jq`, and an agent harness that supports hooks
(Claude Code today).

---

## The problem this solves

You ask an agent to do something substantial. It works for twenty minutes.
Then you have two artifacts, and neither is what you needed:

- **A transcript.** Hundreds of tool calls. Technically complete, practically
  unreadable. Nobody scrolls it.
- **A summary.** Written at the end, by the same agent whose work you are
  trying to check. Readable, but you are taking its word for it.

What is missing is the middle: the ability to see the work while it is
happening, in a form you can glance at rather than audit.

That is not a model capability problem. It is an interface problem, and it has
a boring solution.

## The solution, in one sentence

**Give the agent a document, and put its current activity at the top.**

One markdown file per day. The agent writes into it as it works. Because it is
just a file, you already have the tooling: your editor, your notes app, your
screen recorder, `git diff`.

## Why the top matters

This is the part worth understanding, because everything else follows from it.

Most work logs are written in chronological narrative order: yesterday's
context, today's plan, then the work. That is the natural way to write a
document and the wrong way to build a live one.

The top of a document is the part visible without scrolling. It is what you see
when you glance at a second monitor, and it is what lands in frame when you hit
record. If current activity is 300 lines down, the document is an archive: true,
complete, and never looked at.

Move the work block above the context block and nothing else changes, but the
document becomes something you watch instead of something you file.

```
┌─────────────────────────────┐
│  header, date, links        │
├─────────────────────────────┤
│  ## Live Feed          ◀────┼── updates every tool call
│  ## Work                    │
│  ## Decisions               │   the work block
│  ## Commits                 │   (what is happening now)
│  ## Session Log             │
├─────────────────────────────┤
│  ## Context                 │
│  ## Research                │   the context block
│  ## Notes                   │   (read once, refer back)
│  ## Next                    │
│  ## Links                   │
└─────────────────────────────┘
```

## Setup

```bash
pip install "novasystem[coworking]"
novasystem coworking init
novasystem coworking install-hook
novasystem coworking doctor
```

`doctor` should report everything ok:

```
  workspace      ~/.novasystem/coworking (ok)
  hook script    ~/.claude/hooks/live-feed.sh (ok)
  executable     ok
  wired events   PostToolUse, Stop
  jq available   ok
```

If `jq available` says MISSING, install it (`brew install jq`,
`apt install jq`). Without it the recording path silently does nothing, which
is the one failure mode that looks like success.

### Point it at notes you already read

The default workspace is `~/.novasystem/coworking`. That is fine, but the layer
works better aimed at a directory you already open every day:

```bash
export NOVA_COWORKING_DIR=~/Vault/Daily      # Obsidian, Logseq, anything
```

Put that in your shell profile. The hook reads the same variable.

## Using it

Once the hook is installed there is nothing to run. Work normally and the
Live Feed fills in.

Two things are worth doing by hand, because tool calls cannot express them.

**Say what you are doing.** Tool calls tell you what was touched, never what
for. The `Now:` headline is the line a viewer actually reads:

```bash
novasystem coworking focus "wiring the Stripe webhook"
```

**Say what you noticed.** When something happens that a tool call does not
explain:

```bash
novasystem coworking note "webhook secret was never set in prod"
```

**Close the session.** One foldable entry, so tomorrow starts from something:

```bash
novasystem coworking log "shipped webhook handling" \
  --change "added signature verification" \
  --change "backfilled the missing prod secret" \
  --next "monitor the first live charge"
```

## Auditing what you left behind

The failure mode of agent work is not usually a wrong answer. It is an
unfinished one: the code written but not committed, the decision made but not
recorded, the schema changed in one place and not the other.

```bash
novasystem coworking audit --since 09:45
```

Ten checks, each independent. A check that raises is reported as a finding
rather than crashing the run, because an audit that dies on check three has
told you less than one that reports the failure and continues.

**Always pass `--since`.** Several agents commonly share one repo. Without a
cutoff, the report credits your session with another session's dirty tree, and
a real finding gets buried in noise you know is not yours.

## Making it yours

The section schema is data, not code. Write `~/.novasystem/coworking.json`:

```json
{
  "root": "~/Vault/Daily",
  "sections": [
    {"name": "live_feed", "header": "Live Feed",  "block": "work"},
    {"name": "shipped",   "header": "Shipped",    "block": "work"},
    {"name": "blocked",   "header": "Blocked",    "block": "work"},
    {"name": "inbox",     "header": "Inbox",      "block": "context",
     "writable": false}
  ]
}
```

`writable: false` marks a section as yours. An agent that can rewrite your own
notes is a worse collaborator, not a more capable one.

Changing the schema does nothing to documents already written. Bring them
along:

```bash
novasystem coworking migrate --all           # dry run, shows the plan
novasystem coworking migrate --all --write   # apply
```

The migration verifies every section body is byte-identical before it writes,
and refuses rather than half-applying. Sections you added by hand that the
schema does not know about are kept, never dropped.

## How the live feed actually works

Worth knowing, because the design explains the constraints.

```
agent tool call
      │
      ▼
PostToolUse hook  ──►  append one JSON line     (bash + jq, ~10ms)
      │
      └──────────────►  detached render          (~500ms, off the hot path)
                              │
                              ▼
                        rebuild the section, replace it whole
```

**Why the split?** Importing Python costs roughly half a second. Paying that on
every `Read` would be felt immediately. Recording is therefore pure shell, and
the expensive part runs detached where nobody waits on it.

**Why rebuild rather than append?** Because appends compound their mistakes.
Double fires, races between two sessions, and hand edits all produce the same
correct document when every render regenerates from the log.

**Noise control.** Consecutive runs of read-only tools collapse into one
counted row (`Read ×7`). Twelve consecutive reads are one act of research, not
twelve events worth of screen space. The window holds fourteen rows and tells
you how many it trimmed.

## Screen recording it

This works well on camera, which was part of the point.

1. Set `NOVA_COWORKING_DIR` to a folder open in your notes app.
2. Open today's file, scrolled to the top.
3. Set a focus headline so the first line says what the session is about.
4. Record the document, not the terminal.

The feed updates roughly half a second behind each action, which reads as live
without being frantic.

## Troubleshooting

**Nothing appears in the Live Feed.**
Run `novasystem coworking doctor`. Most often `jq` is missing or the hook is
not executable. Check `<workspace>/hook-errors.log`.

**The feed is behind.**
`novasystem coworking render` rebuilds immediately. If it keeps lagging, look
for a stale `.render.lock` directory in the feed folder; `audit` reports it.

**A heading got swallowed into a callout.**
`novasystem coworking audit` catches this. It means something wrote a section
without preserving the trailing separator. Version 0.2.0 fixed the two known
causes; if you see it, the document text will show a `##` line directly under
a `>` line.

**Two agents are writing at once.**
Expected, and handled. Writes are lock-guarded, and feed rows are tagged with a
short session id when more than one session is active.

## What this is not

It does not sandbox the agent, review its code, or verify correctness. It makes
the work legible. Legibility is a precondition for the rest, not a substitute.

---

**See also**
[Architecture notes](../architecture/coworking-layer.md) ·
[CHANGELOG](../../CHANGELOG.md)
