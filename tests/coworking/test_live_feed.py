"""Tests for the real-time activity feed."""

import json
import tempfile
import unittest
from pathlib import Path

from novasystem.coworking.config import load_config
from novasystem.coworking.document import Document
from novasystem.coworking.live_feed import (
    DETAIL_CHARS,
    MAX_ROWS,
    LiveFeed,
    collapse,
    format_detail,
    shorten_path,
)


class FeedTestCase(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.config = load_config().with_root(Path(self._tmp.name))
        self.doc = Document("2026-07-25", self.config)
        self.doc.create()
        self.feed = LiveFeed("2026-07-25", self.config)

    def tearDown(self):
        self._tmp.cleanup()


class TestRecording(FeedTestCase):

    def test_payload_is_recorded(self):
        self.feed.record_payload({
            "tool_name": "Edit",
            "session_id": "a3f9beef",
            "tool_input": {"file_path": "/a/b/c.py"},
        })
        events = self.feed.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "Edit")
        self.assertEqual(events[0]["sid"], "a3f9")

    def test_alternate_payload_shapes(self):
        self.feed.record_payload({"tool": "Shell",
                                  "input": {"command": "ls"}})
        self.assertEqual(self.feed.read_events()[0]["kind"], "Shell")

    def test_malformed_lines_are_skipped_not_fatal(self):
        self.feed.append("Edit", "a.py")
        with self.feed.path.open("a") as fh:
            fh.write("this is not json\n")
        self.feed.append("Edit", "b.py")
        self.assertEqual(len(self.feed.read_events()), 2)

    def test_append_never_raises_on_a_bad_path(self):
        broken = LiveFeed("2026-07-25", self.config.with_root(
            Path("/proc/nonexistent-should-not-be-writable")))
        broken.append("Edit", "x.py")     # must not raise

    def test_no_events_reads_as_empty(self):
        self.assertEqual(self.feed.read_events(), [])


class TestCollapsing(unittest.TestCase):

    def test_consecutive_quiet_tools_collapse(self):
        events = [{"ts": f"09:00:0{i}", "kind": "Read", "sid": "a",
                   "detail": f"{i}.py"} for i in range(3)]
        events.append({"ts": "09:00:04", "kind": "Bash", "sid": "a",
                       "detail": "ls"})
        rows = collapse(events)
        self.assertEqual([r["count"] for r in rows], [3, 1])

    def test_loud_tools_never_collapse(self):
        events = [{"ts": f"09:00:0{i}", "kind": "Edit", "sid": "a",
                   "detail": "f.py"} for i in range(3)]
        self.assertEqual(len(collapse(events)), 3)

    def test_sessions_never_merge(self):
        events = [
            {"ts": "09:00:01", "kind": "Read", "sid": "aaaa", "detail": "a"},
            {"ts": "09:00:02", "kind": "Read", "sid": "bbbb", "detail": "b"},
            {"ts": "09:00:03", "kind": "Read", "sid": "bbbb", "detail": "c"},
        ]
        self.assertEqual([r["count"] for r in collapse(events)], [1, 2])

    def test_events_without_a_session_still_collapse(self):
        events = [{"ts": "09:00:01", "kind": "Read", "detail": "a"},
                  {"ts": "09:00:02", "kind": "Read", "detail": "b"}]
        self.assertEqual(len(collapse(events)), 1)


class TestFormatting(unittest.TestCase):

    def test_path_shortens_to_two_components(self):
        self.assertEqual(shorten_path("/a/b/c/d/file.py"), "d/file.py")

    def test_bare_filename_survives(self):
        self.assertEqual(shorten_path("file.py"), "file.py")

    def test_bash_detail_drops_a_leading_cd(self):
        self.assertEqual(format_detail("Bash", "cd /tmp/x && git status"),
                         "git status")

    def test_detail_truncates(self):
        out = format_detail("Bash", "x" * 400)
        self.assertLessEqual(len(out), DETAIL_CHARS)

    def test_backticks_are_neutralised(self):
        self.assertNotIn("`", format_detail("Bash", "echo `whoami`"))

    def test_newlines_are_collapsed(self):
        self.assertNotIn("\n", format_detail("Bash", "one\ntwo"))

    def test_empty_detail_stays_empty(self):
        self.assertEqual(format_detail("Bash", ""), "")


class TestRendering(FeedTestCase):

    def test_idle_when_nothing_recorded(self):
        self.assertIn("Idle", self.feed.render_markdown())

    def test_rows_render_newest_first(self):
        self.feed.append("Edit", "first.py")
        self.feed.append("Edit", "second.py")
        body = self.feed.render_markdown()
        self.assertLess(body.index("second.py"), body.index("first.py"))

    def test_window_is_capped_and_reports_the_trim(self):
        for i in range(MAX_ROWS + 6):
            self.feed.append("Edit", f"file{i}.py")
        body = self.feed.render_markdown()
        self.assertIn("earlier rows trimmed", body)
        rows = [l for l in body.splitlines() if "**Edit**" in l]
        self.assertEqual(len(rows), MAX_ROWS)

    def test_focus_headline_appears(self):
        self.feed.set_focus("porting the layer")
        self.assertIn("**Now:** porting the layer", self.feed.render_markdown())

    def test_session_tags_only_when_more_than_one_session(self):
        self.feed.append("Edit", "a.py", sid="aaaa")
        self.assertNotIn("⟨aaaa⟩", self.feed.render_markdown())
        self.feed.append("Edit", "b.py", sid="bbbb")
        self.assertIn("⟨bbbb⟩", self.feed.render_markdown())

    def test_every_line_stays_inside_the_callout(self):
        self.feed.append("Bash", "one\ntwo")
        self.feed.set_focus("multi\nline focus")
        for line in self.feed.render_markdown().splitlines():
            if line.strip():
                self.assertTrue(line.startswith(">"), f"escaped: {line!r}")

    def test_singular_action_label(self):
        self.feed.append("Edit", "a.py")
        self.assertIn("1 action ", self.feed.render_markdown())


class TestRenderToDocument(FeedTestCase):

    def test_render_writes_the_section(self):
        self.feed.append("Edit", "a.py")
        self.assertEqual(self.feed.render()["status"], "written")
        self.assertIn("a.py", self.doc.read_section("live_feed"))

    def test_render_preserves_the_next_heading(self):
        self.feed.append("Edit", "a.py")
        self.feed.render()
        text = self.doc.read()
        idx = text.index("## Work")
        self.assertNotIn(">", text[idx - 4:idx])

    def test_repeated_renders_stay_stable(self):
        self.feed.append("Edit", "a.py")
        for _ in range(3):
            self.feed.render()
        self.assertEqual(self.doc.read().count("## Work"), 1)
        self.assertNotIn("---\n\n---", self.doc.read())

    def test_render_recreates_a_deleted_section_in_the_right_place(self):
        self.doc.path.write_text(
            self.doc.read().replace("## Live Feed\n", "", 1))
        self.feed.append("Edit", "a.py")
        self.feed.render()
        headers = self.doc.headers()
        self.assertIn("## Live Feed", headers)
        self.assertLess(headers.index("## Live Feed"), headers.index("## Work"))

    def test_render_skips_when_there_is_no_document(self):
        feed = LiveFeed("2026-01-01", self.config)
        self.assertEqual(feed.render()["status"], "skipped")

    def test_dry_run_does_not_write(self):
        self.feed.append("Edit", "a.py")
        before = self.doc.read()
        self.assertEqual(self.feed.render(dry_run=True)["status"], "dry-run")
        self.assertEqual(self.doc.read(), before)


if __name__ == "__main__":
    unittest.main()
