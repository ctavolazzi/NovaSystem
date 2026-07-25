"""Tests for the preservation interlock.

The centrepiece is test_replays_the_real_af0dde2_shape, which feeds the actual
file counts from the commit that wiped NovaSystem-Codex through the assessor and
asserts it would have been blocked. A guardrail that cannot stop the incident it
was built for is decoration.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from novasystem.persona.guardrail import (  # noqa: E402
    Authorization,
    Preservation,
    PreservationRefused,
    SnapshotFailed,
    Verdict,
    assess_tree_deletion,
)


@pytest.fixture()
def guard(tmp_path):
    root = tmp_path / "work"
    root.mkdir()
    return Preservation(root, tmp_path / "journal")


def write(root: Path, name: str, text: str) -> Path:
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


# ------------------------------------------------- the core distinction

def test_atomic_write_alone_would_destroy_the_file(guard, tmp_path):
    """Baseline: this is what the guardrail exists to prevent."""
    p = write(guard.root, "precious.md", "important\n" * 1000)
    before = len(p.read_text())
    Preservation._atomic_write(p, "", "utf-8")  # the unguarded primitive
    assert len(p.read_text()) == 0
    assert before == 10000, "atomicity destroyed the file cleanly"


def test_guarded_write_refuses_the_same_operation(guard):
    p = write(guard.root, "precious.md", "important\n" * 1000)
    with pytest.raises(PreservationRefused) as ei:
        guard.guarded_write(p, "", actor="dce", reason="tidy up")
    assert p.read_text() != "", "file must be untouched after refusal"
    assert ei.value.impact.verdict is Verdict.BLOCKED
    assert ei.value.impact.ratio_removed == 1.0


def test_snapshot_is_taken_even_when_refused(guard):
    """Order matters: snapshot first, assess second."""
    p = write(guard.root, "precious.md", "important\n" * 1000)
    with pytest.raises(PreservationRefused) as ei:
        guard.guarded_write(p, "", actor="dce", reason="tidy up")
    snap = ei.value.impact.snapshot_id
    assert snap is not None
    assert guard.restore_bytes(snap).decode() == "important\n" * 1000


# --------------------------------------------------------- thresholds

def test_small_edit_is_safe(guard):
    p = write(guard.root, "doc.md", "x" * 1000)
    impact = guard.guarded_write(p, "x" * 950, actor="dce", reason="trim")
    assert impact.verdict is Verdict.SAFE
    assert p.read_text() == "x" * 950


def test_moderate_removal_is_review_but_proceeds(guard):
    p = write(guard.root, "doc.md", "x" * 1000)
    impact = guard.guarded_write(p, "x" * 700, actor="dce", reason="cut section")
    assert impact.verdict is Verdict.REVIEW
    assert len(p.read_text()) == 700, "REVIEW warns, it does not block"


def test_growing_a_file_is_always_safe(guard):
    p = write(guard.root, "doc.md", "x" * 100)
    impact = guard.guarded_write(p, "x" * 5000, actor="dce", reason="expand")
    assert impact.verdict is Verdict.SAFE
    assert impact.ratio_removed == 0.0


def test_new_file_is_safe(guard):
    impact = guard.guarded_write(
        guard.root / "new.md", "hello", actor="dce", reason="create"
    )
    assert impact.verdict is Verdict.SAFE
    assert impact.snapshot_id is None


# ------------------------------------------------------ authorization

def test_authorization_permits_the_exact_operation(guard):
    p = write(guard.root, "doc.md", "x" * 1000)
    auth = Authorization(str(p), approved_bytes_removed=1000,
                         approved_by="ctavolazzi", reason="confirmed rewrite")
    impact = guard.guarded_write(p, "", actor="dce", reason="rewrite",
                                 authorization=auth)
    assert impact.verdict is Verdict.BLOCKED, "verdict still records the risk"
    assert p.read_text() == ""


def test_authorization_for_a_smaller_impact_does_not_cover_a_bigger_one(guard):
    """An approval cannot be replayed against a larger blast radius."""
    p = write(guard.root, "doc.md", "x" * 1000)
    auth = Authorization(str(p), approved_bytes_removed=600,
                         approved_by="ctavolazzi", reason="partial")
    with pytest.raises(PreservationRefused):
        guard.guarded_write(p, "", actor="dce", reason="all of it",
                            authorization=auth)
    assert len(p.read_text()) == 1000


def test_authorization_for_another_path_does_not_transfer(guard):
    a = write(guard.root, "a.md", "x" * 1000)
    write(guard.root, "b.md", "y" * 1000)
    auth = Authorization(str(a), approved_bytes_removed=99999,
                         approved_by="ctavolazzi", reason="only a")
    with pytest.raises(PreservationRefused):
        guard.guarded_write(guard.root / "b.md", "", actor="dce",
                            reason="reuse token", authorization=auth)


# ------------------------------------------------------------ escaping

def test_cannot_write_outside_root(guard, tmp_path):
    outside = tmp_path / "elsewhere.md"
    outside.write_text("not yours")
    with pytest.raises(PreservationRefused, match="outside guarded root"):
        guard.guarded_write(outside, "", actor="dce", reason="reach out")
    assert outside.read_text() == "not yours"


def test_cannot_escape_root_with_dotdot(guard, tmp_path):
    outside = tmp_path / "elsewhere.md"
    outside.write_text("not yours")
    sneaky = guard.root / ".." / "elsewhere.md"
    with pytest.raises(PreservationRefused, match="outside guarded root"):
        guard.guarded_write(sneaky, "", actor="dce", reason="traverse")
    assert outside.read_text() == "not yours"


# -------------------------------------------------------------- deletes

def test_guarded_delete_snapshots_then_refuses_large(guard):
    p = write(guard.root, "doc.md", "x" * 1000)
    with pytest.raises(PreservationRefused) as ei:
        guard.guarded_delete(p, actor="dce", reason="cleanup")
    assert p.exists()
    assert guard.restore_bytes(ei.value.impact.snapshot_id).decode() == "x" * 1000


def test_guarded_delete_with_authorization_recovers_from_journal(guard):
    p = write(guard.root, "doc.md", "x" * 1000)
    auth = Authorization(str(p), 1000, "ctavolazzi", "intentional")
    impact = guard.guarded_delete(p, actor="dce", reason="intentional",
                                  authorization=auth)
    assert not p.exists()
    assert guard.restore_bytes(impact.snapshot_id).decode() == "x" * 1000


def test_snapshot_of_missing_path_is_none(guard):
    assert guard.snapshot(guard.root / "nope.md") is None


def test_restore_unknown_snapshot_raises(guard):
    with pytest.raises(SnapshotFailed):
        guard.restore_bytes("deadbeef" * 8)


# ----------------------------------------------- the af0dde2 regression

# Real numbers, measured from the commit that wiped NovaSystem-Codex:
#   git merge-base HEAD origin/dev  ->  8aaaa7c  ->  806 tracked files
#   af0dde2 "fresh start"           ->             702 tracked files
# Global removal is only 12.9%, but 12 subtrees went to zero.
AF0DDE2_WIPED_SUBTREES = [
    "novasystem/utils", "novasystem/tools", "novasystem/core",
    "novasystem/database", "novasystem/strategies", "novasystem/domain",
    "novasystem/config", "novasystem/cli", "novasystem/ui",
    "novasystem/session", "novasystem/api", "novasystem/mcp",
]
AF0DDE2_SUBTREE_SIZES = [14, 11, 8, 7, 6, 5, 4, 4, 3, 3, 3, 2]


def _af0dde2_file_lists():
    """Reconstruct the shape of the commit: 806 -> 702 tracked files.

    70 of the removed files sit in the 12 subtrees that went to zero. The
    remaining 34 came out of directories that survived, which is what keeps the
    global ratio low and makes this a faithful test rather than a flattering one.
    """
    wiped = []
    for sub, n in zip(AF0DDE2_WIPED_SUBTREES, AF0DDE2_SUBTREE_SIZES):
        wiped += [f"{sub}/mod{i}.py" for i in range(n)]
    assert len(wiped) == 70

    # A large surviving area that loses 34 of its files but stays populated.
    thinned_before = [f"archive/old{i}.py" for i in range(200)]
    thinned_after = thinned_before[34:]

    survivors = [f"docs/keep{i}.md" for i in range(806 - len(wiped)
                                                   - len(thinned_before))]

    before = wiped + thinned_before + survivors
    after = thinned_after + survivors
    return before, after


def test_replays_the_real_af0dde2_shape_and_blocks_it():
    before, after = _af0dde2_file_lists()
    assert len(before) == 806
    assert len(after) == 702

    impact = assess_tree_deletion(before, after)

    # The global signal alone would have waved this through.
    assert impact.global_ratio < 0.15
    # The subtree signal catches it.
    assert impact.worst_ratio == 1.0
    assert len(impact.wiped_subtrees) == 12
    assert impact.verdict is Verdict.BLOCKED, (
        "the guardrail must stop the exact incident it was built for"
    )


def test_global_only_check_would_have_missed_it():
    """Documents why the naive design is wrong, so it does not come back."""
    before, after = _af0dde2_file_lists()
    naive_ratio = (len(before) - len(after)) / len(before)
    assert naive_ratio < 0.50, "a 50% global threshold does not fire"
    assert naive_ratio < 0.25, "a 25% global threshold does not fire either"


def test_single_file_move_is_not_flagged_as_a_wipe():
    """min_subtree_files keeps ordinary refactors quiet."""
    before = [f"pkg/mod{i}.py" for i in range(20)] + ["solo/only.py"]
    after = [f"pkg/mod{i}.py" for i in range(20)] + ["moved/only.py"]
    impact = assess_tree_deletion(before, after)
    assert impact.verdict is Verdict.SAFE


def test_ordinary_growth_is_safe():
    before = [f"pkg/mod{i}.py" for i in range(20)]
    after = before + [f"pkg/new{i}.py" for i in range(5)]
    assert assess_tree_deletion(before, after).verdict is Verdict.SAFE


def test_wiping_one_real_package_blocks_even_if_repo_is_huge():
    before = [f"pkg/mod{i}.py" for i in range(5)] + [
        f"other/f{i}.py" for i in range(5000)
    ]
    after = [f"other/f{i}.py" for i in range(5000)]
    impact = assess_tree_deletion(before, after)
    assert impact.global_ratio < 0.002
    assert impact.verdict is Verdict.BLOCKED
    assert impact.wiped_subtrees == ("pkg",)
