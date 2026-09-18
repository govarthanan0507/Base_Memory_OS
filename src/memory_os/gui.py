"""Chat-styled desktop GUI shell — E1/E2 delivery, per UI_TRD.md.

Native Qt widgets, not QWebEngineView (per UI_DEBATE.md's reconvene
addendum) — no QWebChannel bridge; the three functions the design
names (`submit_query`, `start_scan`, `respond_to_candidate`) are
direct calls into the existing continuity.py/project_classification.py/
core.py logic, wired to Qt widget signals.

Two-pane layout (project list + chat), per the human gate's follow-up
request: a left sidebar of projects, selecting one scopes the chat to
that project (queries answer about it directly, and typed messages
are logged as a project event — DISCOVERY_PROTOCOL.md's "update the
memory towards the project" ask). Visual style is a light, white-chat
theme deliberately inspired by (not copying) modern chat UIs — an
own accent color, not a specific product's brand palette.

Requires the optional `gui` extra (`pip install base-memory-os[gui]`).
Never imported by cli.py at module load time, so the CLI stays usable
without PySide6 installed at all.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .continuity import render_project_reentry_brief, submit_query
from .core import MemoryStore
from .logging_setup import get_logger
from .project_classification import classify_artifacts_against_projects, list_candidate_details

logger = get_logger(__name__)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_LIST_ITEM_RE = re.compile(r"^-\s+(.*)$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")

# One own accent color, deliberately not matching a specific product's
# brand palette (a structural-difference discipline this project
# already applies to reused designs elsewhere, e.g.
# WORKERS/Frontend-Developer's anti-UI-copying rule).
_ACCENT = "#3E6FEF"
_ACCENT_HOVER = "#2F58C9"

_STYLE_SHEET = f"""
QMainWindow {{
    background-color: #FFFFFF;
}}
#sidebar {{
    background-color: #F7F7F8;
    border-right: 1px solid #E5E5E5;
}}
#appTitle {{
    font-size: 15px;
    font-weight: 600;
    color: #1A1A1A;
    padding: 16px 14px 10px 14px;
}}
#projectList {{
    border: none;
    background-color: transparent;
    font-size: 13px;
    outline: none;
}}
#projectList::item {{
    padding: 9px 12px;
    border-radius: 6px;
    color: #353740;
    margin: 1px 6px;
}}
#projectList::item:selected {{
    background-color: #ECECF1;
    color: #1A1A1A;
}}
#projectList::item:hover {{
    background-color: #EFEFF1;
}}
#chatPane, #chatScroll, #messageContainer {{
    background-color: #FFFFFF;
    border: none;
}}
#inputBar {{
    background-color: #FFFFFF;
    border-top: 1px solid #E5E5E5;
}}
#inputLine {{
    border: 1px solid #D9D9E3;
    border-radius: 18px;
    padding: 9px 14px;
    font-size: 13px;
    background-color: #FFFFFF;
    color: #1A1A1A;
}}
#sendButton, #scanButton {{
    border: none;
    border-radius: 16px;
    padding: 9px 16px;
    font-size: 13px;
    color: #FFFFFF;
    background-color: {_ACCENT};
}}
#sendButton:hover, #scanButton:hover {{
    background-color: {_ACCENT_HOVER};
}}
#scanButton {{
    background-color: #6E6E80;
}}
#scanButton:hover {{
    background-color: #57576A;
}}
"""


def _markdown_to_html(raw: str) -> str:
    """Convert the small markdown subset continuity.py's briefing text
    actually uses (#/##  headings, "- " list items, **bold**) into Qt's
    native rich-text HTML. Every text segment is HTML-escaped first,
    so structural characters (#, -, *) are the only markup interpreted
    — arbitrary content (a filename, a project summary) can never
    inject real HTML/rich-text markup.
    """
    out: list[str] = []
    in_list = False
    for line in raw.split("\n"):
        escaped = html.escape(line, quote=False)
        stripped = escaped.strip()
        heading = _HEADING_RE.match(stripped)
        if heading:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            out.append(f"<h{level}>{heading.group(2)}</h{level}>")
            continue
        item = _LIST_ITEM_RE.match(stripped)
        if item:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{item.group(1)}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        out.append("<br>" if not stripped else f"<p>{escaped}</p>")
    if in_list:
        out.append("</ul>")
    return _BOLD_RE.sub(r"<b>\1</b>", "".join(out))


class MessageBubble(QLabel):
    """A single chat message.

    User messages: a light-gray rounded bubble, right-aligned.
    Assistant messages: plain text, no bubble/background, left-aligned
    — the same "no box around the assistant's reply" treatment modern
    chat UIs use, rather than a WhatsApp-style bubble on both sides.
    """

    _USER_MAX_WIDTH = 420
    _ASSISTANT_MAX_WIDTH = 560

    def __init__(self, html_text: str, *, is_user: bool) -> None:
        super().__init__(html_text)
        self.setTextFormat(Qt.RichText)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.setAlignment(Qt.AlignRight if is_user else Qt.AlignLeft)
        if is_user:
            self.setMaximumWidth(self._USER_MAX_WIDTH)
            self.setStyleSheet(
                "QLabel { background-color: #F4F4F5; color: #1A1A1A; "
                "border-radius: 14px; padding: 9px 14px; margin: 6px 0; }"
            )
        else:
            self.setMaximumWidth(self._ASSISTANT_MAX_WIDTH)
            self.setStyleSheet(
                "QLabel { background-color: transparent; color: #1A1A1A; "
                "padding: 4px 0; margin: 6px 0; }"
            )


class CandidateCard(QFrame):
    """A proposed artifact-project mapping, with inline Accept/Reject —
    the GUI's `respond_to_candidate` (UI_TRD.md), wired directly to
    Qt button signals. Never calls `relate()` itself; that happens
    inside `MemoryStore.review_artifact_project_candidate`, only after
    the user clicks a button.
    """

    def __init__(self, store: MemoryStore, candidate: dict) -> None:
        super().__init__()
        self._store = store
        self._candidate_id = candidate["candidate_id"]
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMaximumWidth(420)
        self.setStyleSheet(
            "QFrame { background-color: #FAFAFA; border: 1px solid #E5E5E5; "
            "border-radius: 10px; padding: 4px; margin: 6px 0; }"
        )

        layout = QVBoxLayout(self)
        text = QLabel(
            f"<b>{candidate['artifact_name']}</b> may belong to "
            f"<b>{candidate['project_name']}</b> "
            f"(confidence {candidate['confidence']:.2f})"
        )
        text.setTextFormat(Qt.RichText)
        text.setWordWrap(True)
        text.setStyleSheet("QLabel { color: #1A1A1A; border: none; }")
        layout.addWidget(text)

        buttons = QHBoxLayout()
        self.accept_button = QPushButton("Accept")
        self.reject_button = QPushButton("Reject")
        self.accept_button.setStyleSheet(
            f"QPushButton {{ border: none; border-radius: 12px; padding: 6px 14px; "
            f"color: white; background-color: {_ACCENT}; }}"
        )
        self.reject_button.setStyleSheet(
            "QPushButton { border: 1px solid #D9D9E3; border-radius: 12px; "
            "padding: 6px 14px; color: #1A1A1A; background-color: white; }"
        )
        self.accept_button.clicked.connect(lambda: self._respond("accepted"))
        self.reject_button.clicked.connect(lambda: self._respond("rejected"))
        buttons.addWidget(self.accept_button)
        buttons.addWidget(self.reject_button)
        layout.addLayout(buttons)

    def _respond(self, decision: str) -> None:
        self._store.review_artifact_project_candidate(self._candidate_id, decision)
        logger.info("gui: candidate %s -> %s", self._candidate_id, decision)
        self.accept_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.setStyleSheet(
            "QFrame { background-color: #FAFAFA; border: 1px solid #E5E5E5; "
            "border-radius: 10px; padding: 4px; margin: 6px 0; color: #9A9AA5; }"
        )


class ChatWindow(QMainWindow):
    def __init__(self, store: MemoryStore) -> None:
        super().__init__()
        self.store = store
        self.current_project_id: str | None = None
        self.setWindowTitle("Base Memory OS")
        self.setStyleSheet(_STYLE_SHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_chat_pane(), 1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("Base Memory OS")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        self.project_list = QListWidget()
        self.project_list.setObjectName("projectList")
        # Qt's list/tree views auto-select row 0 the first time they
        # receive keyboard focus (which happens on window.show(), not
        # on construction) — without this, opening the app fires
        # _on_project_selected for whichever project happens to be
        # first, announcing and dumping its brief before the user has
        # done anything. Mouse-click selection (the primary way this
        # sidebar is actually used) does not require focus, so this
        # loses nothing real; only tab/arrow-key focus is disabled.
        self.project_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.refresh_projects()
        self.project_list.currentItemChanged.connect(self._on_project_selected)
        layout.addWidget(self.project_list)
        return sidebar

    def _build_chat_pane(self) -> QWidget:
        chat_pane = QWidget()
        chat_pane.setObjectName("chatPane")
        layout = QVBoxLayout(chat_pane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.message_container = QWidget()
        self.message_container.setObjectName("messageContainer")
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(20, 16, 20, 16)
        self.message_layout.addStretch()
        self.scroll_area.setWidget(self.message_container)
        layout.addWidget(self.scroll_area)

        input_bar = QWidget()
        input_bar.setObjectName("inputBar")
        input_row = QHBoxLayout(input_bar)
        input_row.setContentsMargins(16, 12, 16, 12)
        self.input_line = QLineEdit()
        self.input_line.setObjectName("inputLine")
        self.input_line.setPlaceholderText("Message Base Memory OS…")
        self.input_line.returnPressed.connect(self._on_submit_query)
        send_button = QPushButton("Send")
        send_button.setObjectName("sendButton")
        send_button.clicked.connect(self._on_submit_query)
        scan_button = QPushButton("Scan folder…")
        scan_button.setObjectName("scanButton")
        scan_button.clicked.connect(self._on_scan_folder)
        input_row.addWidget(self.input_line)
        input_row.addWidget(send_button)
        input_row.addWidget(scan_button)
        layout.addWidget(input_bar)
        return chat_pane

    def refresh_projects(self) -> None:
        self.project_list.clear()
        for row in self.store.list_projects(limit=200):
            item = QListWidgetItem(row["name"])
            item.setData(Qt.ItemDataRole.UserRole, row["project_id"])
            self.project_list.addItem(item)

    def add_message(self, text: str, *, is_user: bool) -> MessageBubble:
        # User-typed text is escaped only, never markdown-parsed — it's
        # not this product's own output, so it should render as plain
        # text, not be interpreted as markup.
        rendered = html.escape(text, quote=False) if is_user else _markdown_to_html(text)
        bubble = MessageBubble(rendered, is_user=is_user)
        self._insert_row(bubble, is_user=is_user)
        return bubble

    def add_candidate_card(self, candidate: dict) -> CandidateCard:
        card = CandidateCard(self.store, candidate)
        self._insert_row(card, is_user=False)
        return card

    def _insert_row(self, widget: QWidget, *, is_user: bool) -> None:
        # A dedicated row (QHBoxLayout + stretch) rather than the box
        # layout's own alignment flag — a QLabel with wordWrap can
        # otherwise report a stale (too-small) height the first time
        # it's placed with an alignment flag directly in a QVBoxLayout,
        # visibly truncating multi-line text. Wrapping in its own row
        # sizes it normally, with no such quirk.
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        if is_user:
            row_layout.addStretch()
            row_layout.addWidget(widget)
        else:
            row_layout.addWidget(widget)
            row_layout.addStretch()
        self.message_layout.insertWidget(self.message_layout.count() - 1, row)

    def message_widgets(self) -> list[QWidget]:
        """Every `MessageBubble`/`CandidateCard` currently shown, in
        order — unwraps each one from its alignment row.
        """
        widgets: list[QWidget] = []
        for i in range(self.message_layout.count()):
            item = self.message_layout.itemAt(i).widget()
            if item is None:
                continue
            if isinstance(item, (MessageBubble, CandidateCard)):
                widgets.append(item)
                continue
            found = item.findChild(MessageBubble) or item.findChild(CandidateCard)
            if found is not None:
                widgets.append(found)
        return widgets

    def _on_project_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            self.current_project_id = None
            return
        self.current_project_id = current.data(Qt.ItemDataRole.UserRole)
        self.add_message(f"Now chatting about {current.text()}", is_user=False)
        self.add_message(render_project_reentry_brief(self.store, self.current_project_id), is_user=False)

    def _on_submit_query(self) -> None:
        text = self.input_line.text().strip()
        if not text:
            return
        self.input_line.clear()
        self.add_message(text, is_user=True)
        if self.current_project_id:
            # Scoped to a selected project: the note is logged against
            # it (DISCOVERY_PROTOCOL.md's "update the memory towards
            # the project" ask), and the reply is that project's own
            # freshly-recomputed re-entry brief — it now includes the
            # note just logged, so the reply visibly reflects it.
            self.store.add_project_event(self.current_project_id, "chat_note", text)
            logger.info("gui: chat_note logged for project %s", self.current_project_id)
            reply = render_project_reentry_brief(self.store, self.current_project_id)
        else:
            reply = submit_query(self.store, text)
            logger.info("gui: submit_query(%r)", text)
        self.add_message(reply, is_user=False)

    def _on_scan_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select a folder to scan")
        if not folder:
            return
        self.add_message(f"Scan {folder}", is_user=True)
        result = classify_artifacts_against_projects(folder, self.store)
        logger.info(
            "gui: start_scan(%s) -> %d artifact(s), %d candidate(s)",
            folder, result.artifacts_registered, result.candidates_created,
        )
        self.add_message(
            f"Registered {result.artifacts_registered} artifact(s): "
            f"{result.candidates_created} candidate(s) proposed, "
            f"{result.unclassified_count} unclassified, {len(result.skipped)} skipped",
            is_user=False,
        )
        for candidate in list_candidate_details(self.store, "candidate"):
            self.add_candidate_card(candidate)


def run_gui(db_path: str | Path = ".memory-os/memory.db") -> int:
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    store = MemoryStore(db_path)
    window = ChatWindow(store)
    window.resize(760, 640)
    window.show()
    try:
        return app.exec()
    finally:
        store.close()


__all__ = ["CandidateCard", "ChatWindow", "MessageBubble", "run_gui"]
