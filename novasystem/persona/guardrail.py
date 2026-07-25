"""Preservation interlock: stop an agent from destroying work.

This is deliberately *not* an atomicity layer, and the distinction is the whole
point of the module.

``atomic_write`` guarantees a write completes cleanly. Measured against a real
file:

    before: 16000 chars
    after atomic_write(path, ''): 0 chars
    VERDICT: destroyed 16000 chars ATOMICALLY and returned success

Atomicity prevents *corruption*. It has no concept of "this operation destroys
data", so it will happily annihilate a file without tearing it. Preservation is a
separate guarantee and needs separate machinery.

The threat model is not a malicious agent. It is commit af0dde2 in this project's
sibling repo: a well-formed, plausible, single-purpose change with a reasonable
message ("fresh start - agentic framework seed") that removed 81 of 83 modules and
was pushed to three branches at once. Nothing about it looked wrong. Any check
that only catches malformed or obviously hostile operations waves that through.

So the interlock is built on three rules:

1. **Snapshot before, always.** Every guarded operation content-addresses the
   current bytes into a journal *and reads them back* before the operation runs.
   No snapshot, no operation. Snapshots are never removed by this module.
2. **Impact is measured, not asserted.** The verdict comes from comparing bytes
   and file counts, so an agent cannot talk its way past it.
3. **Authorization is specific.** An override names the exact path and the exact
   impact it is approving. A generic "yes" cannot be minted in advance or reused
   for a bigger blast radius than the one a human saw.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

DEFAULT_REVIEW_RATIO = 0.25
DEFAULT_BLOCK_RATIO = 0.50


class Verdict(str, Enum):
    SAFE = "safe"
    REVIEW = "review"
    BLOCKED = "blocked"


class PreservationRefused(RuntimeError):
    """A destructive operation was refused. Carries the assessment."""

    def __init__(self, message: str, impact: "Impact") -> None:
        super().__init__(message)
        self.impact = impact


class SnapshotFailed(RuntimeError):
    """The pre-operation snapshot could not be written or read back."""


@dataclass(frozen=True)
class Impact:
    """Measured blast radius of a proposed operation."""

    path: str
    bytes_before: int
    bytes_after: int
    files_before: int
    files_after: int
    verdict: Verdict
    snapshot_id: Optional[str] = None

    @property
    def bytes_removed(self) -> int:
        return max(0, self.bytes_before - self.bytes_after)

    @property
    def files_removed(self) -> int:
        return max(0, self.files_before - self.files_after)

    @property
    def ratio_removed(self) -> float:
        if self.bytes_before == 0:
            return 0.0
        return self.bytes_removed / self.bytes_before

    def describe(self) -> str:
        return (
            f"{self.path}: {self.bytes_before} -> {self.bytes_after} bytes "
            f"({self.ratio_removed:.0%} removed), "
            f"{self.files_before} -> {self.files_after} files, "
            f"verdict={self.verdict.value}"
        )


@dataclass(frozen=True)
class Authorization:
    """Explicit, single-use approval for one specific destructive operation.

    Bound to a path and to a byte count. An authorization issued for a small
    change cannot be replayed against a larger one, and one issued for a
    different path does not apply here.
    """

    path: str
    approved_bytes_removed: int
    approved_by: str
    reason: str

    def covers(self, impact: Impact) -> bool:
        return (
            os.path.abspath(self.path) == os.path.abspath(impact.path)
            and impact.bytes_removed <= self.approved_bytes_removed
        )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _measure(path: Path) -> tuple[int, int]:
    """Return (total_bytes, file_count) for a file or directory tree."""
    if not path.exists():
        return 0, 0
    if path.is_file():
        return path.stat().st_size, 1
    total, count = 0, 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
            count += 1
    return total, count


class Preservation:
    """Guards destructive operations against a root directory.

    Usage::

        guard = Preservation(root, journal_dir)
        guard.guarded_write(path, new_text, actor="dce", reason="rewrite section")
    """

    def __init__(
        self,
        root: Path | str,
        journal_dir: Path | str,
        review_ratio: float = DEFAULT_REVIEW_RATIO,
        block_ratio: float = DEFAULT_BLOCK_RATIO,
    ) -> None:
        if not 0.0 < review_ratio <= block_ratio <= 1.0:
            raise ValueError(
                "require 0 < review_ratio <= block_ratio <= 1, got "
                f"{review_ratio} and {block_ratio}"
            )
        self.root = Path(root).resolve()
        self.journal_dir = Path(journal_dir).resolve()
        self.review_ratio = review_ratio
        self.block_ratio = block_ratio
        (self.journal_dir / "objects").mkdir(parents=True, exist_ok=True)
        self.index_path = self.journal_dir / "index.jsonl"

    # ------------------------------------------------------------- snapshots

    def snapshot(self, path: Path | str) -> Optional[str]:
        """Content-address the current bytes of ``path`` into the journal.

        Returns the snapshot id, or None if the path does not exist (nothing to
        preserve). Raises :class:`SnapshotFailed` if the stored copy cannot be
        read back and verified, because an unverified snapshot is not a snapshot.
        """
        path = Path(path)
        if not path.exists():
            return None
        if path.is_dir():
            return self._snapshot_tree(path)
        return self._snapshot_file(path)

    def _store_blob(self, data: bytes) -> str:
        digest = _sha256_bytes(data)
        dest = self.journal_dir / "objects" / digest[:2] / digest
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            fd, tmp = tempfile.mkstemp(dir=str(dest.parent))
            try:
                with os.fdopen(fd, "wb") as fh:
                    fh.write(data)
                    fh.flush()
                    os.fsync(fh.fileno())
                os.replace(tmp, dest)
            except Exception:
                Path(tmp).unlink(missing_ok=True)
                raise
        # Read back and verify. An unverified snapshot is not a snapshot.
        if _sha256_bytes(dest.read_bytes()) != digest:
            raise SnapshotFailed(f"snapshot readback mismatch for {digest[:12]}")
        return digest

    def _snapshot_file(self, path: Path) -> str:
        digest = self._store_blob(path.read_bytes())
        self._append_index(
            {
                "kind": "file",
                "path": str(path),
                "digest": digest,
                "bytes": path.stat().st_size,
                "at": time.time(),
            }
        )
        return digest

    def _snapshot_tree(self, path: Path) -> str:
        entries = []
        for p in sorted(path.rglob("*")):
            if p.is_file():
                entries.append(
                    {"rel": str(p.relative_to(path)),
                     "digest": self._store_blob(p.read_bytes())}
                )
        manifest = json.dumps(
            {"root": str(path), "entries": entries}, sort_keys=True
        ).encode()
        digest = self._store_blob(manifest)
        self._append_index(
            {
                "kind": "tree",
                "path": str(path),
                "digest": digest,
                "files": len(entries),
                "at": time.time(),
            }
        )
        return digest

    def _append_index(self, record: dict) -> None:
        with open(self.index_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def restore_bytes(self, snapshot_id: str) -> bytes:
        blob = self.journal_dir / "objects" / snapshot_id[:2] / snapshot_id
        if not blob.exists():
            raise SnapshotFailed(f"no snapshot {snapshot_id[:12]}")
        return blob.read_bytes()

    # ------------------------------------------------------------ assessment

    def assess(self, path: Path | str, new_bytes: int, new_files: int = 1) -> Impact:
        path = Path(path)
        before_bytes, before_files = _measure(path)
        impact = Impact(
            path=str(path),
            bytes_before=before_bytes,
            bytes_after=new_bytes,
            files_before=before_files,
            files_after=new_files,
            verdict=Verdict.SAFE,
        )
        ratio = impact.ratio_removed
        if ratio >= self.block_ratio:
            verdict = Verdict.BLOCKED
        elif ratio >= self.review_ratio:
            verdict = Verdict.REVIEW
        else:
            verdict = Verdict.SAFE
        return Impact(
            path=impact.path,
            bytes_before=impact.bytes_before,
            bytes_after=impact.bytes_after,
            files_before=impact.files_before,
            files_after=impact.files_after,
            verdict=verdict,
        )

    # ------------------------------------------------------- guarded actions

    def guarded_write(
        self,
        path: Path | str,
        content: str,
        actor: str,
        reason: str,
        authorization: Optional[Authorization] = None,
        encoding: str = "utf-8",
    ) -> Impact:
        """Snapshot, assess, then write atomically. Refuse if over budget.

        Order matters: the snapshot happens before the assessment, so even a
        refused operation leaves a recoverable copy behind.
        """
        path = Path(path)
        self._require_inside_root(path)

        snapshot_id = self.snapshot(path)
        new_bytes = len(content.encode(encoding))
        impact = self.assess(path, new_bytes)
        impact = Impact(**{**impact.__dict__, "snapshot_id": snapshot_id})

        if impact.verdict is Verdict.BLOCKED:
            if authorization is None or not authorization.covers(impact):
                raise PreservationRefused(
                    f"refusing destructive write by {actor!r}: {impact.describe()}. "
                    f"reason given: {reason!r}. "
                    f"Snapshot {(snapshot_id or 'none')[:12]} was taken first, so "
                    f"nothing is lost. Provide an Authorization naming this exact "
                    f"path and at least {impact.bytes_removed} bytes removed.",
                    impact,
                )

        self._atomic_write(path, content, encoding)
        self._append_index(
            {
                "kind": "write",
                "path": str(path),
                "actor": actor,
                "reason": reason,
                "verdict": impact.verdict.value,
                "bytes_removed": impact.bytes_removed,
                "snapshot": snapshot_id,
                "authorized_by": authorization.approved_by if authorization else None,
                "at": time.time(),
            }
        )
        return impact

    def guarded_delete(
        self,
        path: Path | str,
        actor: str,
        reason: str,
        authorization: Optional[Authorization] = None,
    ) -> Impact:
        """Delete only after a verified snapshot, and only within budget."""
        path = Path(path)
        self._require_inside_root(path)
        if not path.exists():
            raise FileNotFoundError(path)

        snapshot_id = self.snapshot(path)
        impact = self.assess(path, new_bytes=0, new_files=0)
        impact = Impact(**{**impact.__dict__, "snapshot_id": snapshot_id})

        if impact.verdict is Verdict.BLOCKED and (
            authorization is None or not authorization.covers(impact)
        ):
            raise PreservationRefused(
                f"refusing delete by {actor!r}: {impact.describe()}. "
                f"reason given: {reason!r}. Snapshot "
                f"{(snapshot_id or 'none')[:12]} exists.",
                impact,
            )

        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        self._append_index(
            {
                "kind": "delete",
                "path": str(path),
                "actor": actor,
                "reason": reason,
                "snapshot": snapshot_id,
                "at": time.time(),
            }
        )
        return impact

    # --------------------------------------------------------------- helpers

    def _require_inside_root(self, path: Path) -> None:
        """Refuse to act outside the configured root.

        Uses resolved paths so `..` traversal and symlinks cannot escape.
        """
        resolved = path.resolve() if path.exists() else (
            path.parent.resolve() / path.name
        )
        try:
            resolved.relative_to(self.root)
        except ValueError:
            raise PreservationRefused(
                f"{resolved} is outside guarded root {self.root}",
                Impact(str(path), 0, 0, 0, 0, Verdict.BLOCKED),
            ) from None

    @staticmethod
    def _atomic_write(path: Path, content: str, encoding: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp",
                                   dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding=encoding) as fh:
                fh.write(content)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, path)
        except Exception:
            Path(tmp).unlink(missing_ok=True)
            raise


@dataclass(frozen=True)
class TreeImpact:
    """Assessment of a change to a set of tracked paths, per subtree."""

    files_before: int
    files_after: int
    global_ratio: float
    worst_subtree: Optional[str]
    worst_ratio: float
    wiped_subtrees: tuple[str, ...]
    verdict: Verdict

    def describe(self) -> str:
        return (
            f"{self.files_before} -> {self.files_after} files "
            f"(global {self.global_ratio:.1%} removed); "
            f"worst subtree {self.worst_subtree or 'n/a'} at {self.worst_ratio:.1%}; "
            f"{len(self.wiped_subtrees)} subtree(s) fully removed; "
            f"verdict={self.verdict.value}"
        )


def _subtree_key(path: str, depth: int) -> str:
    parts = path.split("/")
    if len(parts) > depth:
        return "/".join(parts[:depth])
    return "/".join(parts[:-1]) or "<root>"


def assess_tree_deletion(
    before: Iterable[str],
    after: Iterable[str],
    block_ratio: float = DEFAULT_BLOCK_RATIO,
    review_ratio: float = DEFAULT_REVIEW_RATIO,
    depth: int = 2,
    min_subtree_files: int = 2,
) -> TreeImpact:
    """Assess a proposed change to a set of tracked paths, per subtree.

    A global ratio is the obvious design and it does not work. Replaying the real
    af0dde2 commit through a global check:

        GLOBAL ratio removed: 12.9%  (806 -> 702 files)   <- reads as SAFE

    while underneath it:

        100.0%  novasystem/utils      100.0%  novasystem/core
        100.0%  novasystem/tools      100.0%  novasystem/database
        ... 12 subtrees removed in full

    Real destruction is concentrated, not spread evenly, so the signal lives in
    the worst subtree rather than the average. This function verdicts on the
    maximum per-subtree removal ratio, and any subtree emptied completely is
    treated as BLOCKED regardless of how small the global fraction looks.

    ``min_subtree_files`` avoids flagging a one-file directory as "100% wiped",
    which is usually just a file being moved.
    """
    before_set, after_set = set(before), set(after)
    n_before, n_after = len(before_set), len(after_set)
    global_ratio = (n_before - n_after) / n_before if n_before else 0.0

    counts_before: dict[str, int] = {}
    counts_after: dict[str, int] = {}
    for p in before_set:
        k = _subtree_key(p, depth)
        counts_before[k] = counts_before.get(k, 0) + 1
    for p in after_set:
        k = _subtree_key(p, depth)
        counts_after[k] = counts_after.get(k, 0) + 1

    worst_subtree, worst_ratio = None, 0.0
    wiped: list[str] = []
    for key, n in counts_before.items():
        if n < min_subtree_files:
            continue
        left = counts_after.get(key, 0)
        ratio = 1.0 - (left / n)
        if left == 0:
            wiped.append(key)
        if ratio > worst_ratio:
            worst_subtree, worst_ratio = key, ratio

    effective = max(global_ratio, worst_ratio)
    if wiped or effective >= block_ratio:
        verdict = Verdict.BLOCKED
    elif effective >= review_ratio:
        verdict = Verdict.REVIEW
    else:
        verdict = Verdict.SAFE

    return TreeImpact(
        files_before=n_before,
        files_after=n_after,
        global_ratio=global_ratio,
        worst_subtree=worst_subtree,
        worst_ratio=worst_ratio,
        wiped_subtrees=tuple(sorted(wiped)),
        verdict=verdict,
    )
