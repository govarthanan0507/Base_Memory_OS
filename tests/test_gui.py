import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
except ImportError:  # pragma: no cover - exercised only without the 'gui' extra
    QApplication = None


@unittest.skipUnless(QApplication is not None, "PySide6 ('gui' extra) not installed")
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from memory_os.core import Artifact, MemoryStore, Project

        self.tmp = tempfile.TemporaryDirectory()
        self.store = MemoryStore(Path(self.tmp.name) / "memory.db")
        self.project_id = self.store.add_project(Project("Video Understanding", str(Path(self.tmp.name) / "video")))
        self.artifact_id = self.store.add_artifact(Artifact("collector.py", "code", str(Path(self.tmp.name) / "video" / "collector.py")))

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_message_bubble_alignment(self):
        from memory_os.gui import MessageBubble

        user_bubble = MessageBubble("hi", is_user=True)
        assistant_bubble = MessageBubble("hello", is_user=False)
        self.assertEqual(user_bubble.alignment(), Qt.AlignRight)
        self.assertEqual(assistant_bubble.alignment(), Qt.AlignLeft)
        self.assertEqual(user_bubble.textFormat(), Qt.RichText)

    def test_candidate_card_accept_creates_relation_and_disables_buttons(self):
        from memory_os.core import ArtifactProjectCandidateRecord
        from memory_os.gui import CandidateCard

        candidate_id = self.store.add_artifact_project_candidate(ArtifactProjectCandidateRecord(
            artifact_id=self.artifact_id, project_id=self.project_id, confidence=0.7,
        ))
        card = CandidateCard(self.store, {
            "candidate_id": candidate_id, "artifact_name": "collector.py",
            "project_name": "Video Understanding", "confidence": 0.7,
        })
        card.accept_button.click()

        self.assertFalse(card.accept_button.isEnabled())
        self.assertFalse(card.reject_button.isEnabled())
        self.assertEqual(self.store.related(self.project_id, "contains")[0]["target_id"], self.artifact_id)

    def test_candidate_card_escapes_artifact_and_project_names(self):
        # F-06 (QA finding, PR #11): these two fields come from
        # filenames/project names, not this product's own trusted
        # output - a maliciously or carelessly named file must not
        # inject real HTML structure into the rendered card.
        from memory_os.gui import CandidateCard

        card = CandidateCard(self.store, {
            "candidate_id": "cand-1",
            "artifact_name": "<script>alert(1)</script>.py",
            "project_name": "<img onerror=alert(1) src=x>",
            "confidence": 0.5,
        })
        from PySide6.QtWidgets import QLabel
        text_label = [w for w in card.findChildren(QLabel) if "may belong to" in w.text()]
        self.assertTrue(text_label, "expected to find the card's descriptive QLabel")
        rendered = text_label[0].text()
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<img", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;img", rendered)

    def test_candidate_card_reject_creates_no_relation(self):
        from memory_os.core import ArtifactProjectCandidateRecord
        from memory_os.gui import CandidateCard

        candidate_id = self.store.add_artifact_project_candidate(ArtifactProjectCandidateRecord(
            artifact_id=self.artifact_id, project_id=self.project_id, confidence=0.4,
        ))
        card = CandidateCard(self.store, {
            "candidate_id": candidate_id, "artifact_name": "collector.py",
            "project_name": "Video Understanding", "confidence": 0.4,
        })
        card.reject_button.click()

        self.assertEqual(self.store.related(self.project_id, "contains"), [])

    def test_chat_window_submit_query_adds_user_and_assistant_bubbles(self):
        from memory_os.gui import ChatWindow, MessageBubble

        window = ChatWindow(self.store)
        window.input_line.setText("what's the status of Video Understanding")
        window.input_line.returnPressed.emit()

        bubbles = [w for w in window.message_widgets() if isinstance(w, MessageBubble)]
        self.assertEqual(len(bubbles), 2)
        self.assertIn("what's the status", bubbles[0].text())
        self.assertIn("Video Understanding", bubbles[1].text())

    def test_chat_window_scan_folder_adds_candidate_card(self):
        from memory_os.gui import CandidateCard, ChatWindow

        scan_dir = Path(self.tmp.name) / "downloads"
        scan_dir.mkdir()
        (scan_dir / "video_understanding_notes.md").write_text("video understanding notes", encoding="utf-8")

        window = ChatWindow(self.store)
        with mock.patch("memory_os.gui.QFileDialog.getExistingDirectory", return_value=str(scan_dir)):
            window._on_scan_folder()

        cards = [w for w in window.message_widgets() if isinstance(w, CandidateCard)]
        self.assertEqual(len(cards), 1)

    def test_chat_window_scan_folder_cancelled_dialog_adds_nothing(self):
        from memory_os.gui import ChatWindow

        window = ChatWindow(self.store)
        with mock.patch("memory_os.gui.QFileDialog.getExistingDirectory", return_value=""):
            window._on_scan_folder()

        self.assertEqual(window.message_widgets(), [])

    def test_sidebar_lists_existing_projects(self):
        from memory_os.gui import ChatWindow

        window = ChatWindow(self.store)
        self.assertEqual(window.project_list.count(), 1)
        item = window.project_list.item(0)
        self.assertEqual(item.text(), "Video Understanding")
        self.assertEqual(item.data(Qt.ItemDataRole.UserRole), self.project_id)

    def test_showing_the_window_does_not_auto_select_a_project(self):
        # Regression test: Qt's list views auto-select row 0 the first
        # time they receive keyboard focus, which happens on show(),
        # not on construction — this silently announced and dumped a
        # project's brief before any real user action, and no test
        # that skips show() (all the others in this file) could catch
        # it.
        from memory_os.gui import ChatWindow

        window = ChatWindow(self.store)
        window.show()
        self.app.processEvents()

        self.assertIsNone(window.current_project_id)
        self.assertEqual(window.message_widgets(), [])

    def test_selecting_a_project_scopes_chat_and_shows_its_brief(self):
        from memory_os.gui import ChatWindow, MessageBubble

        window = ChatWindow(self.store)
        window.project_list.setCurrentRow(0)

        self.assertEqual(window.current_project_id, self.project_id)
        bubbles = [w for w in window.message_widgets() if isinstance(w, MessageBubble)]
        self.assertEqual(len(bubbles), 2)
        self.assertIn("Now chatting about Video Understanding", bubbles[0].text())
        self.assertIn("Video Understanding", bubbles[1].text())

    def test_typed_message_while_project_scoped_logs_a_project_event(self):
        from memory_os.gui import ChatWindow

        window = ChatWindow(self.store)
        window.project_list.setCurrentRow(0)
        window.input_line.setText("remember to refactor the collector module")
        window.input_line.returnPressed.emit()

        events = self.store.list_project_events(self.project_id)
        notes = [e for e in events if e["event_type"] == "chat_note"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["summary"], "remember to refactor the collector module")

    def test_typed_message_with_no_project_scoped_uses_submit_query(self):
        from memory_os.gui import ChatWindow, MessageBubble

        window = ChatWindow(self.store)
        window.input_line.setText("what's the status of Video Understanding")
        window.input_line.returnPressed.emit()

        events = self.store.list_project_events(self.project_id)
        self.assertEqual([e for e in events if e["event_type"] == "chat_note"], [])
        bubbles = [w for w in window.message_widgets() if isinstance(w, MessageBubble)]
        self.assertIn("Video Understanding", bubbles[-1].text())


if __name__ == "__main__":
    unittest.main()
