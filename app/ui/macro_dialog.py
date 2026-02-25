"""MacroDialog — record, edit, and step-run command macros.

Lifecycle:
    1. User opens dialog via MACRO button in the main window.
    2. Build commands with the Message Creator, click "Capture Current" to
       append each one to the editor.  Commands are NOT sent during capture.
    3. Give the macro a name and click "Save Macro" → written to data/macros.json,
       tagged with the current device name and an ISO timestamp.
    4. Load any saved macro from the "Saved:" dropdown.  The editor is fully
       editable — add, delete, or reorder lines freely.
    5. Click "▶ Step Send" to fire the current command.  The button disables
       until a reply arrives (forwarded by MainWindow.log_reply).  Then click
       again for the next command.  "■ Reset" returns to step 1.

Macros are per-device: only macros recorded for the currently selected device
appear in the dropdown.
"""

import json
import os
import re
from datetime import datetime

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)
from PySide6.QtCore import Qt

# Path to the macros storage file, relative to this module.
_MACROS_FILE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "macros.json")
)


# ---------------------------------------------------------------------------
# Low-level file helpers
# ---------------------------------------------------------------------------

def _load_macros():
    """Return the full macros list from disk, or [] on any error."""
    try:
        with open(_MACROS_FILE, "r") as f:
            return json.load(f).get("macros", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_macros(macros):
    """Write the full macros list to disk."""
    os.makedirs(os.path.dirname(_MACROS_FILE), exist_ok=True)
    with open(_MACROS_FILE, "w") as f:
        json.dump({"macros": macros}, f, indent=2)


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class MacroDialog(QDialog):
    """Record, edit, and step-execute command macros."""

    def __init__(self, get_current_message, send_fn, device_name="", parent=None):
        """
        Args:
            get_current_message: Callable → str.  Returns the message currently
                assembled in the main window's Message Creator.
            send_fn:             Callable(str).  Sends a UDP command string.
            device_name:         Name of the currently selected device (e.g.
                                 "capstanDrive").  Used to tag and filter macros.
            parent:              Parent QWidget (the main window).
        """
        super().__init__(parent)
        self.get_current_message = get_current_message
        self.send_fn = send_fn
        self.device_name = device_name

        # Step-run state
        self._step_index = 0
        self._step_lines = []
        self._awaiting_reply = False

        self.setWindowTitle(f"Macro Manager — {device_name or 'No device selected'}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(560)

        self._build_ui()
        self._refresh_macro_list()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout()
        root.setSpacing(8)
        root.setContentsMargins(10, 10, 10, 10)
        self.setLayout(root)

        # ── Library row ──────────────────────────────────────────────
        lib_row = QHBoxLayout()
        lib_row.addWidget(QLabel("Saved:"))
        self.macro_combo = QComboBox()
        self.macro_combo.setMinimumWidth(220)
        self.macro_combo.currentIndexChanged.connect(self._on_macro_selected)
        lib_row.addWidget(self.macro_combo, stretch=1)
        self.new_btn = QPushButton("New")
        self.new_btn.setFixedWidth(60)
        self.new_btn.setToolTip("Clear editor to start a new macro")
        self.new_btn.clicked.connect(self._on_new)
        lib_row.addWidget(self.new_btn)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFixedWidth(60)
        self.delete_btn.setToolTip("Delete the selected macro from the library")
        self.delete_btn.clicked.connect(self._on_delete)
        lib_row.addWidget(self.delete_btn)
        root.addLayout(lib_row)

        # ── Name row ─────────────────────────────────────────────────
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter macro name…")
        name_row.addWidget(self.name_edit, stretch=1)
        root.addLayout(name_row)

        # ── Command editor ───────────────────────────────────────────
        root.addWidget(QLabel("Commands (one per line):"))
        self.command_editor = QPlainTextEdit()
        self.command_editor.setPlaceholderText(
            "STEPPER,stop\nLED,redLED,off\nSTEPPER,home"
        )
        self.command_editor.setMinimumHeight(180)
        self.command_editor.textChanged.connect(self._on_editor_changed)
        root.addWidget(self.command_editor)

        # ── Capture / Save row ───────────────────────────────────────
        action_row = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Current")
        self.capture_btn.setToolTip(
            "Append the command currently assembled in the Message Creator"
        )
        self.capture_btn.clicked.connect(self._on_capture)
        action_row.addWidget(self.capture_btn)
        action_row.addStretch()
        self.save_btn = QPushButton("Save Macro")
        self.save_btn.clicked.connect(self._on_save)
        action_row.addWidget(self.save_btn)
        root.addLayout(action_row)

        # ── Separator ────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        root.addWidget(sep)

        # ── Step-run row ─────────────────────────────────────────────
        step_row = QHBoxLayout()
        self.step_label = QLabel("Step: —")
        self.step_label.setMinimumWidth(200)
        step_row.addWidget(self.step_label, stretch=1)
        self.step_btn = QPushButton("▶  Step Send")
        self.step_btn.setFixedWidth(110)
        self.step_btn.setToolTip("Send the current step command; waits for reply")
        self.step_btn.clicked.connect(self._on_step_send)
        step_row.addWidget(self.step_btn)
        self.reset_btn = QPushButton("■  Reset")
        self.reset_btn.setFixedWidth(80)
        self.reset_btn.setToolTip("Return to step 1")
        self.reset_btn.clicked.connect(self._on_reset)
        step_row.addWidget(self.reset_btn)
        root.addLayout(step_row)

        # ── Step reply box ───────────────────────────────────────────
        self.step_reply = QTextEdit()
        self.step_reply.setReadOnly(True)
        self.step_reply.setFixedHeight(58)
        self.step_reply.setPlaceholderText("Device reply will appear here…")
        self.step_reply.setStyleSheet(
            "background: #e6f7ff; border: 1px solid #ccc; padding: 4px;"
        )
        root.addWidget(self.step_reply)

        # ── Close ────────────────────────────────────────────────────
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(self.close)
        close_row.addWidget(close_btn)
        root.addLayout(close_row)

        self._update_step_display()

    # ------------------------------------------------------------------
    # Library helpers
    # ------------------------------------------------------------------

    def _refresh_macro_list(self):
        """Reload macros.json and populate the combo box (device-filtered)."""
        self.macro_combo.blockSignals(True)
        self.macro_combo.clear()
        self.macro_combo.addItem("— select a macro —", userData=None)
        self._macros = _load_macros()
        for i, m in enumerate(self._macros):
            if not self.device_name or m.get("device") == self.device_name:
                label = m.get("name", f"Macro {i}")
                self.macro_combo.addItem(label, userData=i)
        self.macro_combo.blockSignals(False)

    def _get_selected_macro_index(self):
        """Return the index into self._macros for the current combo selection, or None."""
        return self.macro_combo.currentData()

    # ------------------------------------------------------------------
    # UI event handlers — library
    # ------------------------------------------------------------------

    def _on_macro_selected(self, _combo_index):
        idx = self._get_selected_macro_index()
        if idx is None:
            return
        m = self._macros[idx]
        self.name_edit.setText(m.get("name", ""))
        self.command_editor.setPlainText("\n".join(m.get("commands", [])))
        self._on_reset()

    def _on_new(self):
        """Clear the editor so the user can start a new macro from scratch."""
        self.macro_combo.blockSignals(True)
        self.macro_combo.setCurrentIndex(0)
        self.macro_combo.blockSignals(False)
        self.name_edit.clear()
        self.command_editor.clear()
        self._on_reset()

    def _on_capture(self):
        """Append the currently assembled main-window message to the editor."""
        msg = self.get_current_message()
        if not msg:
            return
        if "\u25a1" in msg:  # □ placeholder means incomplete field
            QMessageBox.warning(
                self, "Incomplete Command",
                "Fill in all required fields in the Message Creator first."
            )
            return
        existing = self.command_editor.toPlainText().rstrip("\n")
        self.command_editor.setPlainText(
            (existing + "\n" + msg).lstrip("\n")
        )

    def _on_save(self):
        """Save (or overwrite) the macro in macros.json."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Name Required", "Enter a name for this macro.")
            return

        lines = [
            ln.strip()
            for ln in self.command_editor.toPlainText().splitlines()
            if ln.strip()
        ]
        if not lines:
            QMessageBox.warning(self, "Empty Macro", "Add at least one command.")
            return

        macros = _load_macros()

        # Overwrite if same name + device already exists
        existing_idx = next(
            (
                i for i, m in enumerate(macros)
                if m.get("name") == name and m.get("device") == self.device_name
            ),
            None,
        )
        entry = {
            "name": name,
            "device": self.device_name,
            "created": datetime.now().isoformat(timespec="seconds"),
            "commands": lines,
        }
        if existing_idx is not None:
            macros[existing_idx] = entry
        else:
            macros.append(entry)

        _save_macros(macros)
        self._refresh_macro_list()

        # Re-select the saved macro in the combo
        for i in range(self.macro_combo.count()):
            if self.macro_combo.itemText(i) == name:
                self.macro_combo.blockSignals(True)
                self.macro_combo.setCurrentIndex(i)
                self.macro_combo.blockSignals(False)
                break

    def _on_delete(self):
        """Delete the currently selected macro."""
        idx = self._get_selected_macro_index()
        if idx is None:
            return
        name = self._macros[idx].get("name", "this macro")
        reply = QMessageBox.question(
            self, "Delete Macro",
            f"Delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        macros = _load_macros()
        del macros[idx]
        _save_macros(macros)
        self._on_new()
        self._refresh_macro_list()

    # ------------------------------------------------------------------
    # UI event handlers — step-run
    # ------------------------------------------------------------------

    def _on_editor_changed(self):
        """Keep step display in sync when the editor text changes."""
        self._update_step_display()

    def _on_step_send(self):
        """Fire the current step command and wait for a reply."""
        if self._awaiting_reply:
            return  # Must wait for reply (or reset) before advancing

        # Re-parse lines in case the editor was edited since last step
        lines = [
            ln.strip()
            for ln in self.command_editor.toPlainText().splitlines()
            if ln.strip()
        ]
        if not lines:
            return

        self._step_lines = lines

        if self._step_index >= len(self._step_lines):
            self.step_reply.setPlainText("All commands sent.  Click ■ Reset to run again.")
            return

        cmd = self._step_lines[self._step_index]
        self.send_fn(cmd)
        self._awaiting_reply = True
        self.step_btn.setEnabled(False)
        self.step_reply.setPlainText("Waiting for reply…")
        self._update_step_display()

    def _on_reset(self):
        """Return to step 1."""
        self._step_index = 0
        self._step_lines = []
        self._awaiting_reply = False
        self.step_btn.setEnabled(True)
        self.step_reply.clear()
        self._update_step_display()

    def _update_step_display(self):
        """Refresh the step label to show [current/total] next command."""
        lines = [
            ln.strip()
            for ln in self.command_editor.toPlainText().splitlines()
            if ln.strip()
        ]
        total = len(lines)
        if total == 0:
            self.step_label.setText("Step: —")
            return
        if self._step_index >= total:
            self.step_label.setText(f"Step: done ({total}/{total})")
            return
        cmd = lines[self._step_index]
        self.step_label.setText(f"[{self._step_index + 1}/{total}]  {cmd}")

    # ------------------------------------------------------------------
    # Called by MainWindow when a UDP reply arrives
    # ------------------------------------------------------------------

    def receive_reply(self, raw_msg):
        """Forward a UDP reply into the step reply box and advance the step.

        Called by MainWindow.log_reply() when the dialog is open and in
        step-run mode (_awaiting_reply == True).

        Args:
            raw_msg: The raw message string from UDPClientThread.message_received.
                     Could be "Received from ('ip', port): payload" or already
                     translated to "From name: payload".
        """
        if not self._awaiting_reply:
            return

        # Strip the "Received from …" wrapper if still present
        match = re.match(r"Received from \('[\d.]+', \d+\): (.*)", raw_msg, re.DOTALL)
        payload = match.group(1) if match else raw_msg

        self.step_reply.setPlainText(payload)
        self._awaiting_reply = False
        self._step_index += 1
        self._update_step_display()
        # Re-enable Step Send unless we've finished the list
        self.step_btn.setEnabled(self._step_index < len(self._step_lines))
