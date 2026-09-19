"""Desktop application shell — routes through `service.py` only.

Per the Windows-application conversion requirements: `GUI -> service
layer -> core`, never `GUI -> subprocess -> CLI`. Every action here
(chat, project selection, folder scan, candidate review, import,
search) calls a `MemoryOSService` method; nothing in this module
touches `MemoryStore`/`continuity.py`/etc. directly any more.

Two audiences, one window: everyday use never shows a raw ID, a
traceback, or the word "SQLite" — those are gated behind
Settings -> Advanced -> Developer Mode, a persistent (`QSettings`)
per-user preference, off by default.

Requires the optional `gui` extra (`pip install base-memory-os[gui]`).
Never imported by cli.py at module load time, so the CLI stays usable
without PySide6 installed at all.
"""

from __future__ import annotations

import html
import re
import traceback
from functools import wraps
from typing import Callable

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .logging_setup import get_logger
from .service import MemoryOSService

logger = get_logger(__name__)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_LIST_ITEM_RE = re.compile(r"^-\s+(.*)$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")

# One own accent color, deliberately not matching a specific product's
# brand palette (a structural-difference discipline this project
# already applies to reused designs elsewhere).
_ACCENT = "#3E6FEF"
_ACCENT_HOVER = "#2F58C9"

_STYLE_SHEET = f"""
QMainWindow, QDialog {{
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
#sectionLabel {{
    font-size: 11px;
    font-weight: 600;
    color: #8A8A93;
    padding: 14px 14px 4px 14px;
    letter-spacing: 0.5px;
}}
#projectList {{
    border: none;
    background-color: transparent;
    font-size: 13px;
    outline: none;
}}
#projectList::item, QListWidget::item {{
    padding: 9px 12px;
    border-radius: 6px;
    color: #353740;
    margin: 1px 6px;
}}
#projectList::item:selected, QListWidget::item:selected {{
    background-color: #ECECF1;
    color: #1A1A1A;
}}
#projectList::item:hover, QListWidget::item:hover {{
    background-color: #EFEFF1;
}}
#navButton {{
    text-align: left;
    border: none;
    background-color: transparent;
    padding: 9px 14px;
    font-size: 13px;
    color: #353740;
    border-radius: 6px;
    margin: 1px 6px;
}}
#navButton:hover {{
    background-color: #EFEFF1;
}}
#chatPane, #chatScroll, #messageContainer, #memoryPane, #searchPane {{
    background-color: #FFFFFF;
    border: none;
}}
#inputBar {{
    background-color: #FFFFFF;
    border-top: 1px solid #E5E5E5;
}}
#inputLine, #searchLine {{
    border: 1px solid #D9D9E3;
    border-radius: 18px;
    padding: 9px 14px;
    font-size: 13px;
    background-color: #FFFFFF;
    color: #1A1A1A;
}}
#sendButton, #scanButton, #primaryButton {{
    border: none;
    border-radius: 16px;
    padding: 9px 16px;
    font-size: 13px;
    color: #FFFFFF;
    background-color: {_ACCENT};
}}
#sendButton:hover, #scanButton:hover, #primaryButton:hover {{
    background-color: {_ACCENT_HOVER};
}}
#scanButton {{
    background-color: #6E6E80;
}}
#scanButton:hover {{
    background-color: #57576A;
}}
#settingsButton {{
    border: none;
    background-color: transparent;
    font-size: 16px;
    padding: 4px 10px;
}}
#settingsButton:hover {{
    background-color: #EFEFF1;
    border-radius: 6px;
}}
"""

_ORG, _APP = "BaseMemoryOS", "BaseMemoryOS"


def _settings() -> QSettings:
    # The two-argument QSettings(organization, application) constructor
    # always uses NativeFormat regardless of QSettings.setDefaultFormat,
    # which made this silently write to real OS-level config storage
    # even under test (a QSettings.setPath override in a test only
    # takes effect for a format explicitly requested here). Explicit
    # IniFormat/UserScope is honored by setPath, cross-platform, and a
    # predictable plain file either way.
    return QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, _ORG, _APP)


def developer_mode_enabled() -> bool:
    return _settings().value("developer_mode", False, type=bool)


def _guarded(label: str) -> Callable:
    """Wrap a GUI action handler so an unexpected exception never
    reaches the user as a traceback. Always logged in full; shown to
    the user only as a plain "something went wrong" message, with the
    real detail available only when Developer Mode is on.
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - deliberate top-level guard
                logger.exception("gui: %s failed", label)
                detail = "".join(traceback.format_exception(exc)) if developer_mode_enabled() else str(exc)
                box = QMessageBox(self)
                box.setIcon(QMessageBox.Icon.Warning)
                box.setWindowTitle("Something went wrong")
                box.setText(f"Base Memory OS could not complete this operation.\n\n({label})")
                box.setDetailedText(detail)
                box.exec()
                return None

        return wrapped

    return decorator


def _markdown_to_html(raw: str) -> str:
    """Convert the small markdown subset the service's rendered text
    actually uses (#/##  headings, "- " list items, **bold**) into
    Qt's native rich-text HTML. Every text segment is HTML-escaped
    first, so structural characters (#, -, *) are the only markup
    interpreted — arbitrary content (a filename, a project summary)
    can never inject real HTML/rich-text markup.
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
    Assistant messages: plain text, no bubble/background, left-aligned.
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


def _confidence_word(confidence: float) -> str:
    if confidence >= 0.75:
        return "High confidence"
    if confidence >= 0.45:
        return "Medium confidence"
    return "Low confidence"


class CandidateCard(QFrame):
    """A proposed file-to-project match, in plain language — no
    candidate/artifact IDs shown unless Developer Mode is on. Routes
    the user's decision through the service layer only
    (`review_artifact_candidate`), never touching the store directly.
    """

    def __init__(self, service: MemoryOSService, candidate: dict) -> None:
        super().__init__()
        self._service = service
        self._candidate_id = candidate["candidate_id"]
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMaximumWidth(420)
        self.setStyleSheet(
            "QFrame { background-color: #FAFAFA; border: 1px solid #E5E5E5; "
            "border-radius: 10px; padding: 4px; margin: 6px 0; }"
        )

        layout = QVBoxLayout(self)
        # F-06 (QA finding, PR #11): these two fields come from
        # filenames/project names on disk, not this product's own
        # trusted output - they must be escaped, or a maliciously/
        # carelessly named file can inject HTML structure into this
        # card.
        artifact_name = html.escape(candidate["artifact_name"], quote=False)
        project_name = html.escape(candidate["project_name"], quote=False)
        text = QLabel(
            f"Base Memory OS thinks <b>{artifact_name}</b> may belong to "
            f"<b>{project_name}</b>."
        )
        text.setTextFormat(Qt.RichText)
        text.setWordWrap(True)
        text.setStyleSheet("QLabel { color: #1A1A1A; border: none; }")
        layout.addWidget(text)

        confidence_label = QLabel(_confidence_word(candidate["confidence"]))
        confidence_label.setStyleSheet("QLabel { color: #8A8A93; font-size: 11px; border: none; }")
        layout.addWidget(confidence_label)
        if developer_mode_enabled():
            dev_label = QLabel(
                f"candidate_id={self._candidate_id}  confidence={candidate['confidence']:.2f}"
            )
            dev_label.setStyleSheet("QLabel { color: #B5B5BD; font-size: 10px; border: none; }")
            layout.addWidget(dev_label)

        buttons = QHBoxLayout()
        self.accept_button = QPushButton("Remember")
        self.reject_button = QPushButton("Ignore")
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
        try:
            self._service.review_artifact_candidate(self._candidate_id, decision)
        except Exception:
            logger.exception("gui: candidate review failed")
            QMessageBox.warning(self, "Something went wrong", "Base Memory OS could not save that decision.")
            return
        logger.info("gui: candidate %s -> %s", self._candidate_id, decision)
        self.accept_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.setStyleSheet(
            "QFrame { background-color: #FAFAFA; border: 1px solid #E5E5E5; "
            "border-radius: 10px; padding: 4px; margin: 6px 0; color: #9A9AA5; }"
        )


class OnboardingDialog(QDialog):
    """Shown once, on the very first launch (tracked in `QSettings`,
    not the memory database — reinstalling the app or wiping the DB
    doesn't itself bring this back for a returning user).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to Base Memory OS")
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(14)

        title = QLabel("Welcome to Base Memory OS")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1A1A1A;")
        layout.addWidget(title)

        subtitle = QLabel("Your personal memory and continuity system.")
        subtitle.setStyleSheet("color: #6E6E80; font-size: 13px;")
        layout.addWidget(subtitle)

        body = QLabel(
            "Base Memory OS helps you preserve:\n"
            "• conversations\n"
            "• projects\n"
            "• decisions\n"
            "• ideas\n"
            "• important context and working history\n\n"
            "Everything stays on this computer — nothing is sent anywhere."
        )
        body.setWordWrap(True)
        body.setStyleSheet("color: #353740; font-size: 13px;")
        layout.addWidget(body)

        get_started = QPushButton("Get Started")
        get_started.setObjectName("primaryButton")
        get_started.clicked.connect(self.accept)
        layout.addWidget(get_started)


class SettingsDialog(QDialog):
    def __init__(self, service: MemoryOSService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self.setWindowTitle("Settings")
        self.setFixedWidth(420)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        layout.addWidget(self._heading("Storage"))
        location = QLabel(f"Your memory is stored locally on this computer:\n{service.db_path}")
        location.setWordWrap(True)
        location.setStyleSheet("color: #353740; font-size: 12px;")
        layout.addWidget(location)

        layout.addWidget(self._heading("AI Processing"))
        processing = QLabel(
            "Local only — no AI model or external API is used today. "
            "Matching and search run entirely on this device, on stored text."
        )
        processing.setWordWrap(True)
        processing.setStyleSheet("color: #353740; font-size: 12px;")
        layout.addWidget(processing)

        layout.addWidget(self._heading("Privacy"))
        privacy = QLabel("Your memory never leaves this computer unless you export it yourself.")
        privacy.setWordWrap(True)
        privacy.setStyleSheet("color: #353740; font-size: 12px;")
        layout.addWidget(privacy)

        layout.addWidget(self._heading("Advanced"))
        self.dev_mode_checkbox = QCheckBox("Enable Developer Mode (shows internal IDs and diagnostics)")
        self.dev_mode_checkbox.setChecked(developer_mode_enabled())
        self.dev_mode_checkbox.toggled.connect(self._on_dev_mode_toggled)
        layout.addWidget(self.dev_mode_checkbox)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    @staticmethod
    def _heading(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-size: 12px; font-weight: 600; color: #8A8A93; margin-top: 6px;")
        return label

    def _on_dev_mode_toggled(self, checked: bool) -> None:
        _settings().setValue("developer_mode", checked)


class MemoryPage(QWidget):
    """Human-readable list of stored memories. Deliberately does not
    invent categories (Preferences/Decisions/Goals) this product does
    not actually compute — each memory is shown with the type it was
    actually stored under, honestly, not a fabricated classification.
    """

    def __init__(self, service: MemoryOSService) -> None:
        super().__init__()
        self._service = service
        self.setObjectName("memoryPane")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        title = QLabel("Your Memory")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1A1A1A;")
        layout.addWidget(title)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        memories = self._service.store.list_memories(limit=200)
        if not memories:
            self.list_widget.addItem("Nothing remembered yet.")
            return
        for row in memories:
            label = row["memory_type"].replace("_", " ").capitalize()
            self.list_widget.addItem(f"[{label}] {row['content']}")


class SearchPage(QWidget):
    def __init__(self, service: MemoryOSService) -> None:
        super().__init__()
        self._service = service
        self.setObjectName("searchPane")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        title = QLabel("Search your memory")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1A1A1A;")
        layout.addWidget(title)

        row = QHBoxLayout()
        self.search_line = QLineEdit()
        self.search_line.setObjectName("searchLine")
        self.search_line.setPlaceholderText("Search your memory…")
        self.search_line.returnPressed.connect(self._on_search)
        button = QPushButton("Search")
        button.setObjectName("sendButton")
        button.clicked.connect(self._on_search)
        row.addWidget(self.search_line)
        row.addWidget(button)
        layout.addLayout(row)

        self.results_widget = QListWidget()
        layout.addWidget(self.results_widget)

    @_guarded("search")
    def _on_search(self) -> None:
        query = self.search_line.text().strip()
        self.results_widget.clear()
        if not query:
            return
        results = self._service.search_memories(query, limit=20)
        if not results:
            self.results_widget.addItem("No matches found.")
            return
        for row in results:
            self.results_widget.addItem(f"{row['content']}  —  ({row['source']})")


class MainWindow(QMainWindow):
    """Chat is the primary interaction (project-scoped or general),
    with Projects/Memory/Search reachable from the sidebar and
    Settings from the toolbar. Everything routes through
    `MemoryOSService` — see module docstring.
    """

    def __init__(self, service: MemoryOSService) -> None:
        super().__init__()
        self.service = service
        self.current_project_id: str | None = None
        self.setWindowTitle("Base Memory OS")
        self.setStyleSheet(_STYLE_SHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.chat_page = self._build_chat_pane()
        self.memory_page = MemoryPage(self.service)
        self.search_page = SearchPage(self.service)
        self.stack.addWidget(self.chat_page)   # index 0
        self.stack.addWidget(self.memory_page)  # index 1
        self.stack.addWidget(self.search_page)  # index 2
        root.addWidget(self.stack, 1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        title = QLabel("Base Memory OS")
        title.setObjectName("appTitle")
        header.addWidget(title)
        header.addStretch()
        settings_button = QPushButton("⚙")
        settings_button.setObjectName("settingsButton")
        settings_button.setToolTip("Settings")
        settings_button.clicked.connect(self._on_open_settings)
        header.addWidget(settings_button)
        layout.addLayout(header)

        layout.addWidget(self._nav_button("Memory", lambda: self.stack.setCurrentIndex(1)))
        layout.addWidget(self._nav_button("Search", lambda: self.stack.setCurrentIndex(2)))

        projects_label = QLabel("PROJECTS")
        projects_label.setObjectName("sectionLabel")
        layout.addWidget(projects_label)

        self.project_list = QListWidget()
        self.project_list.setObjectName("projectList")
        # Qt's list/tree views auto-select row 0 the first time they
        # receive keyboard focus (which happens on window.show(), not
        # on construction) — without this, opening the app fires
        # _on_project_selected for whichever project happens to be
        # first, announcing and dumping its brief before the user has
        # done anything.
        self.project_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.refresh_projects()
        self.project_list.currentItemChanged.connect(self._on_project_selected)
        layout.addWidget(self.project_list)

        add_folder = self._nav_button("+ Add Project Folder…", self._on_add_project_folder)
        layout.addWidget(add_folder)
        return sidebar

    @staticmethod
    def _nav_button(text: str, on_click: Callable[[], None]) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.clicked.connect(on_click)
        return button

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
        import_button = QPushButton("Import conversations…")
        import_button.setObjectName("scanButton")
        import_button.clicked.connect(self._on_import_chatgpt_export)
        input_row.addWidget(self.input_line)
        input_row.addWidget(send_button)
        input_row.addWidget(scan_button)
        input_row.addWidget(import_button)
        layout.addWidget(input_bar)
        return chat_pane

    def refresh_projects(self) -> None:
        self.project_list.clear()
        for summary in self.service.list_projects(limit=200):
            item = QListWidgetItem(summary.name)
            item.setData(Qt.ItemDataRole.UserRole, summary.project_id)
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
        card = CandidateCard(self.service, candidate)
        self._insert_row(card, is_user=False)
        return card

    def _insert_row(self, widget: QWidget, *, is_user: bool) -> None:
        # A dedicated row (QHBoxLayout + stretch) rather than the box
        # layout's own alignment flag — a QLabel with wordWrap can
        # otherwise report a stale (too-small) height the first time
        # it's placed with an alignment flag directly in a QVBoxLayout,
        # visibly truncating multi-line text.
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

    @_guarded("open project")
    def _on_project_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            self.current_project_id = None
            return
        self.stack.setCurrentIndex(0)
        self.current_project_id = current.data(Qt.ItemDataRole.UserRole)
        self.add_message(f"Now chatting about {current.text()}", is_user=False)
        self.add_message(self.service.project_brief_text(self.current_project_id), is_user=False)

    @_guarded("send message")
    def _on_submit_query(self) -> None:
        text = self.input_line.text().strip()
        if not text:
            return
        self.input_line.clear()
        self.add_message(text, is_user=True)
        reply = self.service.ask(text, project_id=self.current_project_id)
        self.add_message(reply, is_user=False)

    @_guarded("scan folder")
    def _on_scan_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select a folder to scan")
        if not folder:
            return
        self.add_message(f"Scan {folder}", is_user=True)
        result = self.service.classify_folder(folder)
        logger.info(
            "gui: scan_folder(%s) -> %d artifact(s), %d candidate(s)",
            folder, result.artifacts_registered, result.candidates_created,
        )
        self.add_message(
            f"Scanned that folder: found {result.artifacts_registered} file(s), "
            f"{result.candidates_created} possible project match(es) to review below.",
            is_user=False,
        )
        for candidate in self.service.list_artifact_candidates("candidate"):
            self.add_candidate_card(candidate)
        self.refresh_projects()

    @_guarded("add project folder")
    def _on_add_project_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select a folder to add as a project source")
        if not folder:
            return
        discovered = self.service.scan_projects(folder)
        self.refresh_projects()
        QMessageBox.information(
            self, "Scan complete",
            f"{len(discovered)} project(s) found in that folder. No files were moved or deleted.",
        )

    @_guarded("import conversations")
    def _on_import_chatgpt_export(self) -> None:
        path, _filter = QFileDialog.getOpenFileName(
            self, "Choose your ChatGPT export file", "", "JSON files (*.json)"
        )
        if not path:
            return
        count = self.service.import_chatgpt_export(path)
        QMessageBox.information(
            self, "Import complete", f"{count} conversation(s) imported."
        )

    def _on_open_settings(self) -> None:
        dialog = SettingsDialog(self.service, self)
        dialog.exec()
        # Developer Mode may have just been toggled - candidate cards
        # rendered after this point should reflect it; nothing already
        # on screen needs to change retroactively.


def run_app(service: MemoryOSService) -> int:
    """The desktop application's real entry point. Handles first-
    launch onboarding, then opens the main window. `service` is
    already initialized (its own constructor creates the database and
    schema if missing) — no separate manual init step.
    """
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))

    settings = _settings()
    if not settings.value("onboarding_complete", False, type=bool):
        onboarding = OnboardingDialog()
        onboarding.exec()
        settings.setValue("onboarding_complete", True)

    window = MainWindow(service)
    window.resize(900, 640)
    window.show()
    return app.exec()


# Backward-compatible alias: earlier builds called the main window
# `ChatWindow`. Kept so any external/developer code importing that
# name still works.
ChatWindow = MainWindow


__all__ = [
    "CandidateCard",
    "ChatWindow",
    "MainWindow",
    "MemoryPage",
    "MessageBubble",
    "OnboardingDialog",
    "SearchPage",
    "SettingsDialog",
    "developer_mode_enabled",
    "run_app",
]
