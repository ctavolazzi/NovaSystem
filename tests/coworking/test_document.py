"""Tests for the work log document and its section API.

Every test runs against a temporary workspace. Nothing here reads or writes a
real user's notes.
"""

import tempfile
import unittest
from pathlib import Path

from novasystem.coworking.config import load_config
from novasystem.coworking.document import (
    Document,
    PermissionDenied,
    SectionError,
    SilentNoOp,
    _join_appended,
    _replace_section,
    _split_trailer,
)


class WorkspaceTestCase(unittest.TestCase):
    """Base: a throwaway workspace per test."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.config = load_config().with_root(Path(self._tmp.name))
        self.doc = Document("2026-07-25", self.config)

    def tearDown(self):
        self._tmp.cleanup()


class TestCreation(WorkspaceTestCase):

    def test_create_renders_the_template(self):
        path = self.doc.create()
        self.assertTrue(path.is_file())
        text = path.read_text()
        self.assertIn("date: 2026-07-25", text)
        self.assertNotIn("{{date}}", text)
        self.assertNotIn("{{title}}", text)

    def test_create_is_idempotent(self):
        first = self.doc.create()
        first.write_text(first.read_text() + "\nedited by hand\n")
        self.doc.create()
        self.assertIn("edited by hand", first.read_text())

    def test_date_offset_tokens(self):
        self.doc.create()
        text = self.doc.read()
        self.assertIn("[[2026-07-24]]", text)
        self.assertIn("[[2026-07-26]]", text)

    def test_work_block_comes_before_context_block(self):
        self.doc.create()
        headers = self.doc.headers()
        self.assertLess(headers.index("## Live Feed"), headers.index("## Context"))
        self.assertLess(headers.index("## Session Log"),
                        headers.index("## Context"))

    def test_live_feed_is_the_first_section(self):
        self.doc.create()
        self.assertEqual(self.doc.headers()[0], "## Live Feed")


class TestReadWrite(WorkspaceTestCase):

    def setUp(self):
        super().setUp()
        self.doc.create()

    def test_write_then_read_round_trips(self):
        self.doc.write_section("work", "- ported the layer")
        self.assertEqual(self.doc.read_section("work").strip(),
                         "- ported the layer")

    def test_read_section_strips_the_layout_separator(self):
        self.doc.write_section("work", "- item")
        self.assertNotIn("---", self.doc.read_section("work"))
        self.assertIn("---", self.doc.read_section("work", raw=True))

    def test_unknown_section_raises(self):
        with self.assertRaises(SectionError):
            self.doc.read_section("nope")

    def test_automated_actor_cannot_write_a_reserved_section(self):
        with self.assertRaises(PermissionDenied):
            self.doc.write_section("notes", "agent text", actor="agent")

    def test_human_actor_can_write_a_reserved_section(self):
        self.doc.write_section("notes", "my own note", actor="human")
        self.assertIn("my own note", self.doc.read_section("notes"))

    def test_identical_rewrite_is_not_reported_as_a_no_op(self):
        self.doc.write_section("work", "- same\n")
        self.doc.write_section("work", "- same\n")   # must not raise

    def test_append_adds_a_sibling_entry(self):
        self.doc.write_section("work", "first", mode="append")
        self.doc.write_section("work", "second", mode="append")
        body = self.doc.read_section("work")
        self.assertIn("first", body)
        self.assertIn("second", body)

    def test_bad_mode_rejected(self):
        with self.assertRaises(ValueError):
            self.doc.write_section("work", "x", mode="sideways")

    def test_write_to_absent_section_self_heals(self):
        text = self.doc.read().replace("## Research\n", "")
        self.doc.path.write_text(text)
        self.doc.write_section("research", "recovered")
        self.assertIn("recovered", self.doc.read_section("research"))


class TestStatus(WorkspaceTestCase):

    def setUp(self):
        super().setUp()
        self.doc.create()

    def test_fresh_document_has_no_filled_sections(self):
        self.assertNotIn("filled", set(self.doc.status().values()))

    def test_template_scaffolding_reads_as_template_not_filled(self):
        self.assertEqual(self.doc.status()["context"], "template")

    def test_written_section_reads_as_filled(self):
        self.doc.write_section("work", "- real content")
        self.assertEqual(self.doc.status()["work"], "filled")

    def test_missing_header_reads_as_absent(self):
        self.doc.path.write_text(self.doc.read().replace("## Research\n", ""))
        self.assertEqual(self.doc.status()["research"], "absent")


class TestSessionLog(WorkspaceTestCase):

    def setUp(self):
        super().setUp()
        self.doc.create()

    def test_entry_renders_as_a_callout(self):
        self.doc.append_session_log(focus="ported the layer",
                                    changes=["a", "b"], next_steps="ship")
        body = self.doc.read_section("session_log")
        self.assertIn("[!note]-", body)
        self.assertIn("2 changes", body)
        self.assertIn("ship", body)

    def test_singular_change_label(self):
        self.doc.append_session_log(focus="one thing", changes=["only"])
        self.assertIn("1 change", self.doc.read_section("session_log"))

    def test_multiline_focus_cannot_break_out_of_the_callout(self):
        self.doc.append_session_log(focus="line one\nline two")
        for line in self.doc.read_section("session_log").splitlines():
            if "line two" in line:
                self.assertTrue(line.startswith(">"))

    def test_entries_do_not_nest_inside_each_other(self):
        self.doc.append_session_log(focus="first")
        self.doc.append_session_log(focus="second")
        lines = self.doc.read().splitlines()
        violations = [i for i, (a, b) in enumerate(zip(lines, lines[1:]), 2)
                      if b.startswith("**[") and a.lstrip().startswith(">")]
        self.assertEqual(violations, [])


class TestFrontmatter(WorkspaceTestCase):

    def setUp(self):
        super().setUp()
        self.doc.create()

    def test_update_preserves_other_fields(self):
        self.doc.update_frontmatter({"focus": "release prep"})
        fm = self.doc.read_frontmatter()
        self.assertEqual(fm["focus"], "release prep")
        self.assertEqual(str(fm["date"]), "2026-07-25")

    def test_body_is_untouched(self):
        before = self.doc.read().split("---", 2)[-1]
        self.doc.update_frontmatter({"focus": "x"})
        self.assertEqual(self.doc.read().split("---", 2)[-1], before)


class TestSeparatorHandling(unittest.TestCase):
    """The separator between sections is layout and must survive a write.

    Regression: dropping it let a callout-shaped section swallow the next
    heading via markdown lazy continuation, collapsing the rest of the
    document into one block.
    """

    NOTE = "## Live Feed\n\nold body\n\n---\n\n## Work\n\ntasks\n"

    def test_trailing_rule_survives_a_replace(self):
        out = _replace_section(self.NOTE, "## Live Feed",
                               "> [!abstract]+ Live Feed\n> a row\n")
        self.assertIn("> a row\n\n---\n\n## Work", out)

    def test_next_heading_never_touches_a_quoted_line(self):
        out = _replace_section(self.NOTE, "## Live Feed", "> only a quote\n")
        lines = out.splitlines()
        for i in range(1, len(lines)):
            if lines[i].startswith("## "):
                self.assertFalse(lines[i - 1].lstrip().startswith(">"))

    def test_blank_line_added_when_there_was_no_trailer(self):
        note = "## Live Feed\nold\n## Work\n\ntasks\n"
        out = _replace_section(note, "## Live Feed", "> row\n")
        self.assertIn("> row\n\n## Work", out)

    def test_last_section_still_replaces(self):
        note = "## Live Feed\n\nold body\n"
        out = _replace_section(note, "## Live Feed", "new body\n")
        self.assertIn("new body", out)
        self.assertNotIn("old body", out)

    def test_split_trailer_leaves_content_alone(self):
        content, trailer = _split_trailer("a\n\n---\n\nb\n\n---\n\n")
        self.assertEqual(content, "a\n\n---\n\nb\n")
        self.assertEqual(trailer, "\n---\n\n")

    def test_join_appended_inserts_a_blank_line(self):
        self.assertEqual(_join_appended("> old", "new"), "> old\n\nnew\n")

    def test_join_appended_on_empty_body(self):
        self.assertEqual(_join_appended("", "new"), "new\n")


if __name__ == "__main__":
    unittest.main()
