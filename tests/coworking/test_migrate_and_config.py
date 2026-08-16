"""Tests for layout migration, config resolution, and the hook installer."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from novasystem.coworking import install as installer
from novasystem.coworking import migrate as M
from novasystem.coworking.config import (
    DEFAULT_ROOT,
    ENV_DIR,
    SECTION_SCHEMA,
    load_config,
)
from novasystem.coworking.document import Document

OLD_LAYOUT = """\
---
type: worklog
date: 2026-07-25
---

# Work Log

<!-- /header -->

---

## Context

Yesterday's status.

---

## Work

Task body.

---

## Ad Hoc Section

Something the schema never had.

---

## Links

Links body.
"""


class TestSplitSections(unittest.TestCase):

    def test_preamble_and_blocks(self):
        pre, blocks = M.split_sections(OLD_LAYOUT)
        self.assertIn("# Work Log", pre)
        self.assertNotIn("## Context", pre)
        self.assertEqual([h for h, _ in blocks],
                         ["## Context", "## Work", "## Ad Hoc Section",
                          "## Links"])

    def test_heading_inside_a_code_fence_is_content(self):
        text = OLD_LAYOUT.replace("Task body.",
                                  "```markdown\n## Not A Heading\n```")
        _, blocks = M.split_sections(text)
        self.assertNotIn("## Not A Heading", [h for h, _ in blocks])

    def test_frontmatter_stays_in_the_preamble(self):
        pre, _ = M.split_sections(OLD_LAYOUT)
        self.assertTrue(pre.startswith("---\ntype: worklog"))

    def test_document_without_frontmatter(self):
        pre, blocks = M.split_sections("# Title\n\n## A\n\nbody\n")
        self.assertIn("# Title", pre)
        self.assertEqual(len(blocks), 1)


class TestSeparatorNormalisation(unittest.TestCase):

    def test_strips_rules_on_either_side(self):
        self.assertEqual(M.normalize_body("\n---\n\nbody\n\n"), "body")
        self.assertEqual(M.normalize_body("\nbody\n\n---\n"), "body")

    def test_keeps_a_rule_in_the_middle(self):
        self.assertEqual(M.normalize_body("\na\n\n---\n\nb\n"), "a\n\n---\n\nb")

    def test_strips_every_trailing_rule_not_just_one(self):
        self.assertEqual(M.strip_trailing_rule("body\n\n---\n\n---\n"), "body")

    def test_strips_every_leading_rule(self):
        self.assertEqual(M.strip_leading_rule("\n---\n\n---\n\nbody"), "body")


class TestOrdering(unittest.TestCase):

    SCHEMA = ["## Live Feed", "## Work", "## Context", "## Links"]

    def test_schema_order_wins(self):
        got = M.target_order(["## Context", "## Work", "## Links"], self.SCHEMA)
        self.assertEqual(got, ["## Work", "## Context", "## Links"])

    def test_unknown_sections_are_kept_before_the_tail(self):
        got = M.target_order(["## Context", "## Ad Hoc", "## Links"],
                             self.SCHEMA)
        self.assertEqual(got, ["## Context", "## Ad Hoc", "## Links"])

    def test_tail_stays_last(self):
        got = M.target_order(["## Links", "## Work"], self.SCHEMA)
        self.assertEqual(got[-1], "## Links")


class TestReassembly(unittest.TestCase):

    def setUp(self):
        self.pre, self.blocks = M.split_sections(OLD_LAYOUT)
        self.headers = [h for h, _ in self.blocks]
        self.schema = [s.header for s in SECTION_SCHEMA]
        self.order = M.target_order(self.headers, self.schema)

    def test_work_moves_above_context(self):
        self.assertLess(self.order.index("## Work"),
                        self.order.index("## Context"))

    def test_no_body_is_altered(self):
        out = M.reassemble(self.pre, self.blocks, self.order)
        _, new_blocks = M.split_sections(out)
        before = {h: M.normalize_body(b) for h, b in self.blocks}
        after = {h: M.normalize_body(b) for h, b in new_blocks}
        self.assertEqual(before, after)

    def test_reassembly_is_idempotent(self):
        once = M.reassemble(self.pre, self.blocks, self.order)
        pre2, blocks2 = M.split_sections(once)
        twice = M.reassemble(pre2, blocks2, [h for h, _ in blocks2])
        self.assertEqual(once, twice)

    def test_exactly_one_rule_between_sections(self):
        out = M.reassemble(self.pre, self.blocks, self.order)
        self.assertNotIn("---\n\n---", out)

    def test_ad_hoc_section_is_never_dropped(self):
        out = M.reassemble(self.pre, self.blocks, self.order)
        self.assertIn("Something the schema never had.", out)


class TestMigrateOnDisk(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.config = load_config().with_root(Path(self._tmp.name))
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.config.log_path("2026-07-25")
        self.path.write_text(OLD_LAYOUT)

    def tearDown(self):
        self._tmp.cleanup()

    def test_dry_run_does_not_write(self):
        before = self.path.read_text()
        result = M.migrate_document("2026-07-25", config=self.config)
        self.assertTrue(result["status"].startswith("would-"))
        self.assertEqual(self.path.read_text(), before)

    def test_write_reorders_and_adds_missing_sections(self):
        result = M.migrate_document("2026-07-25", write=True, config=self.config)
        self.assertEqual(result["status"], "reordered")
        self.assertIn("## Live Feed", result["added"])
        headers = Document("2026-07-25", self.config).headers()
        self.assertEqual(headers[0], "## Live Feed")

    def test_second_pass_is_a_no_op(self):
        M.migrate_document("2026-07-25", write=True, config=self.config)
        again = M.migrate_document("2026-07-25", write=True, config=self.config)
        self.assertEqual(again["status"], "unchanged")

    def test_content_survives_the_move(self):
        M.migrate_document("2026-07-25", write=True, config=self.config)
        text = self.path.read_text()
        for phrase in ("Yesterday's status.", "Task body.",
                       "Something the schema never had.", "Links body."):
            self.assertIn(phrase, text)

    def test_missing_document_is_skipped_not_an_error(self):
        result = M.migrate_document("2020-01-01", config=self.config)
        self.assertEqual(result["status"], "skipped")

    def test_migrate_all_covers_every_log(self):
        self.config.log_path("2026-07-24").write_text(OLD_LAYOUT)
        results = M.migrate_all(write=True, config=self.config)
        self.assertEqual(len(results), 2)


class TestConfig(unittest.TestCase):

    def setUp(self):
        self._saved = os.environ.pop(ENV_DIR, None)

    def tearDown(self):
        if self._saved is not None:
            os.environ[ENV_DIR] = self._saved
        else:
            os.environ.pop(ENV_DIR, None)

    def test_default_root_is_not_a_personal_path(self):
        config = load_config(config_path=Path("/nonexistent/config.json"))
        self.assertEqual(config.root, DEFAULT_ROOT)
        self.assertNotIn("Documents", str(config.root))

    def test_environment_overrides_the_default(self):
        os.environ[ENV_DIR] = "/tmp/nova-ws-test"
        config = load_config(config_path=Path("/nonexistent/config.json"))
        self.assertEqual(config.root, Path("/tmp/nova-ws-test"))
        self.assertEqual(config.source, f"${ENV_DIR}")

    def test_argument_beats_environment(self):
        os.environ[ENV_DIR] = "/tmp/from-env"
        config = load_config(root=Path("/tmp/from-arg"),
                             config_path=Path("/nonexistent/config.json"))
        self.assertEqual(config.root, Path("/tmp/from-arg"))

    def test_config_file_is_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "coworking.json"
            cfg.write_text(json.dumps({"root": f"{tmp}/ws"}))
            config = load_config(config_path=cfg)
            self.assertEqual(config.root, Path(f"{tmp}/ws"))

    def test_malformed_config_raises_rather_than_being_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "coworking.json"
            cfg.write_text("{not json")
            with self.assertRaises(ValueError):
                load_config(config_path=cfg)

    def test_custom_sections_are_honoured(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "coworking.json"
            cfg.write_text(json.dumps({"sections": [
                {"name": "feed", "header": "Feed", "block": "work"},
                {"name": "rest", "header": "## Rest", "block": "context"},
            ]}))
            config = load_config(config_path=cfg)
            self.assertEqual(config.headers, ["## Feed", "## Rest"])

    def test_section_missing_a_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "coworking.json"
            cfg.write_text(json.dumps({"sections": [{"header": "## X"}]}))
            with self.assertRaises(ValueError):
                load_config(config_path=cfg)

    def test_duplicate_section_names_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "coworking.json"
            cfg.write_text(json.dumps({"sections": [
                {"name": "a", "header": "## A"},
                {"name": "a", "header": "## B"},
            ]}))
            with self.assertRaises(ValueError):
                load_config(config_path=cfg)

    def test_reserved_sections_are_not_writable(self):
        config = load_config(config_path=Path("/nonexistent/config.json"))
        self.assertNotIn("notes", config.writable)


class TestInstaller(unittest.TestCase):
    """The installer edits a user's settings file, so it is tested hard."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._saved = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = self._tmp.name

    def tearDown(self):
        if self._saved is not None:
            os.environ["CLAUDE_CONFIG_DIR"] = self._saved
        else:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        self._tmp.cleanup()

    def _settings(self):
        return json.loads(installer.settings_path().read_text())

    def test_install_creates_hook_and_wires_settings(self):
        result = installer.install()
        self.assertEqual(result["status"], "installed")
        self.assertTrue(installer.hook_target_path().is_file())
        self.assertTrue(os.access(installer.hook_target_path(), os.X_OK))
        hooks = self._settings()["hooks"]
        self.assertIn("PostToolUse", hooks)
        self.assertIn("Stop", hooks)

    def test_installing_twice_does_not_duplicate(self):
        installer.install()
        installer.install()
        hooks = self._settings()["hooks"]
        self.assertEqual(len(hooks["PostToolUse"]), 1)
        self.assertEqual(len(hooks["Stop"]), 1)

    def test_unrelated_settings_are_preserved(self):
        installer.settings_path().write_text(json.dumps({
            "theme": "dark",
            "hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [
                {"type": "command", "command": "echo mine"}]}]},
        }))
        installer.install()
        settings = self._settings()
        self.assertEqual(settings["theme"], "dark")
        commands = json.dumps(settings["hooks"]["PostToolUse"])
        self.assertIn("echo mine", commands)
        self.assertIn("live-feed.sh", commands)

    def test_malformed_settings_aborts_rather_than_overwriting(self):
        installer.settings_path().write_text("{ not json")
        with self.assertRaises(ValueError):
            installer.install()
        self.assertEqual(installer.settings_path().read_text(), "{ not json")

    def test_dry_run_writes_nothing(self):
        result = installer.install(dry_run=True)
        self.assertEqual(result["status"], "dry-run")
        self.assertFalse(installer.hook_target_path().is_file())
        self.assertFalse(installer.settings_path().is_file())

    def test_uninstall_removes_only_our_entries(self):
        installer.settings_path().write_text(json.dumps({
            "hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [
                {"type": "command", "command": "echo mine"}]}]},
        }))
        installer.install()
        installer.uninstall()
        commands = json.dumps(self._settings().get("hooks", {}))
        self.assertIn("echo mine", commands)
        self.assertNotIn("live-feed.sh", commands)
        self.assertFalse(installer.hook_target_path().is_file())

    def test_status_reports_what_is_installed(self):
        self.assertFalse(installer.status()["hook_installed"])
        installer.install()
        state = installer.status()
        self.assertTrue(state["hook_installed"])
        self.assertEqual(sorted(state["wired_events"]),
                         ["PostToolUse", "Stop"])

    def test_settings_are_backed_up_before_a_change(self):
        installer.settings_path().write_text(json.dumps({"theme": "dark"}))
        result = installer.install()
        self.assertIsNotNone(result["backup"])
        self.assertIn("theme", Path(result["backup"]).read_text())


if __name__ == "__main__":
    unittest.main()
