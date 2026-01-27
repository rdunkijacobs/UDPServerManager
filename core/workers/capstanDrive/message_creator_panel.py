
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QLabel, QPushButton, QLineEdit
from PySide6.QtCore import Signal

class MessageCreatorPanel(QWidget):
    def set_server(self, server):
        """
        Set the current server context for the message creator panel.
        Stores the server dictionary and resets fields if needed.
        """
        self._current_server = server
        # Optionally, clear or reset fields when server changes
        self.clear_fields()

    def clear_fields(self):
        """
        Clear or reset all user-editable fields in the panel.
        """
        self.command_dropdown.setCurrentIndex(0)
        self.instance_dropdown.setCurrentIndex(0)
        self.mode_dropdown.setCurrentIndex(0)
        self.param3_dropdown.setCurrentIndex(0)
        self.param4_dropdown.setCurrentIndex(0)
        self.param3_lineedit.clear()
        self.param4_lineedit.clear()
        self.assembled_output.clear()
        self.response_box.clear()
    send_message_signal = Signal(str)
    def setup_logic(self):
        # Populate command dropdown
        if self._command_dict and 'commands' in self._command_dict:
            self.command_dropdown.addItems(list(self._command_dict['commands'].keys()))
        self.command_dropdown.setCurrentIndex(0)
        self.command_dropdown.currentTextChanged.connect(self.update_command_related_dropdowns)
        self.instance_dropdown.currentTextChanged.connect(self.update_mode_dropdown_on_instance)
        self.mode_dropdown.currentTextChanged.connect(self.update_param3_dropdown_on_mode)
        self.param3_dropdown.currentTextChanged.connect(self.update_assembled_message)
        self.param4_dropdown.currentTextChanged.connect(self.update_assembled_message)
        self.send_button.clicked.connect(self.send_udp_message)
        self.param3_lineedit.editingFinished.connect(self.update_assembled_message)
        self.param4_lineedit.editingFinished.connect(self.update_assembled_message)

    def update_command_related_dropdowns(self, command):
        self.instance_dropdown.blockSignals(True)
        self.mode_dropdown.blockSignals(True)
        self.param3_dropdown.blockSignals(True)
        self.param4_dropdown.blockSignals(True)
        self.instance_dropdown.clear()
        self.mode_dropdown.clear()
        self.param3_dropdown.clear()
        self.param4_dropdown.clear()
        self.instance_dropdown.addItem("Instance...")
        self.mode_dropdown.addItem("Mode...")
        self.param3_dropdown.addItem("Parameter 3...")
        self.param4_dropdown.addItem("Parameter 4...")
        self.mode_dropdown.setEnabled(False)
        self.param3_dropdown.setEnabled(False)
        self.param4_dropdown.setEnabled(False)
        if not command or command == "Command...":
            self.instance_dropdown.setEnabled(False)
            self.instance_dropdown.blockSignals(False)
            self.mode_dropdown.blockSignals(False)
            self.param3_dropdown.blockSignals(False)
            self.param4_dropdown.blockSignals(False)
            return
        has_instance = False
        if self._command_config:
            for entry in getattr(self._command_config, 'COMMAND_COUNTS', []):
                if entry.get('command') == command:
                    for name in entry.get('instances', []):
                        self.instance_dropdown.addItem(name)
                    has_instance = True
                    break
        self.instance_dropdown.setEnabled(has_instance and self.instance_dropdown.count() > 1)
        self.instance_dropdown.blockSignals(False)
        self.mode_dropdown.blockSignals(False)
        self.param3_dropdown.blockSignals(False)
        self.param4_dropdown.blockSignals(False)

    def update_mode_dropdown_on_instance(self, instance):
        self.mode_dropdown.blockSignals(True)
        self.param3_dropdown.blockSignals(True)
        self.param4_dropdown.blockSignals(True)
        self.mode_dropdown.clear()
        self.param3_dropdown.clear()
        self.param4_dropdown.clear()
        self.mode_dropdown.addItem("Mode...")
        self.param3_dropdown.addItem("Parameter 3...")
        self.param4_dropdown.addItem("Parameter 4...")
        self.mode_dropdown.setEnabled(False)
        self.param3_dropdown.setEnabled(False)
        self.param4_dropdown.setEnabled(False)
        command = self.command_dropdown.currentText()
        if not command or command == "Command..." or not instance or instance == "Instance...":
            return
        has_mode = False
        if self._command_dict:
            cmd_info = self._command_dict.get('commands', {}).get(command, {})
            params = cmd_info.get('parameters', [])
            for p in params:
                if p.get('name', '').lower() == 'mode' and p.get('type') == 'enum':
                    for opt in p.get('options', []):
                        self.mode_dropdown.addItem(opt)
                    has_mode = True
        self.mode_dropdown.setEnabled(has_mode and self.mode_dropdown.count() > 1)
        self.mode_dropdown.blockSignals(False)
        self.param3_dropdown.blockSignals(False)
        self.param4_dropdown.blockSignals(False)

    def update_param3_dropdown_on_mode(self, mode):
        command = self.command_dropdown.currentText()
        instance = self.instance_dropdown.currentText()
        if not command or command == "Command..." or not instance or instance == "Instance..." or not mode or mode == "Mode...":
            self.param3_dropdown.blockSignals(True)
            self.param4_dropdown.blockSignals(True)
            self.param3_dropdown.clear()
            self.param4_dropdown.clear()
            self.param3_dropdown.addItem("Parameter 3...")
            self.param4_dropdown.addItem("Parameter 4...")
            self.param3_dropdown.setEnabled(False)
            self.param4_dropdown.setEnabled(False)
            return
        param3_name = "Parameter 3"
        param4_name = "Parameter 4"
        param3_options = []
        param4_options = []
        has_param3 = False
        has_param4 = False
        param3_is_lineedit = False
        param4_is_lineedit = False
        # Map param_number to dropdown for robust message assembly
        # Always rebuild param_dropdown_map fresh for each mode change
        self.param_dropdown_map = {1: self.instance_dropdown, 2: self.mode_dropdown}
        if self._command_dict:
            cmd_info = self._command_dict.get('commands', {}).get(command, {})
            params = cmd_info.get('parameters', [])
            # Only pick the first matching param3/param4 for this mode
            param3 = None
            param4 = None
            for p in params:
                if p.get('param_number') == 3:
                    conds = p.get('condition', [])
                    if isinstance(conds, str):
                        conds = [conds]
                    if not conds or any(f"mode == {mode}" == cond.strip() for cond in conds):
                        param3 = p
                        break
            for p in params:
                if p.get('param_number') == 4:
                    conds = p.get('condition', [])
                    if isinstance(conds, str):
                        conds = [conds]
                    if not conds or any(f"mode == {mode}" == cond.strip() for cond in conds):
                        param4 = p
                        break
            if param3:
                param3_name = param3.get('name', 'Parameter 3')
                if param3.get('type') == 'enum':
                    param3_options = param3.get('options', [])
                    has_param3 = True
                    self.param_dropdown_map[3] = self.param3_dropdown
                    param3_is_lineedit = False
                elif param3.get('type') == 'boolean':
                    param3_options = ["on", "off", "0", "1", "true", "false"]
                    has_param3 = True
                    self.param_dropdown_map[3] = self.param3_dropdown
                    param3_is_lineedit = False
                elif param3.get('type') in ('integer', 'float'):
                    has_param3 = True
                    param3_is_lineedit = True
                    self.param_dropdown_map[3] = self.param3_lineedit
            if param4:
                param4_name = param4.get('name', 'Parameter 4')
                if param4.get('type') == 'enum':
                    param4_options = param4.get('options', [])
                    has_param4 = True
                    self.param_dropdown_map[4] = self.param4_dropdown
                    param4_is_lineedit = False
                elif param4.get('type') in ('integer', 'float'):
                    has_param4 = True
                    param4_is_lineedit = True
                    self.param_dropdown_map[4] = self.param4_lineedit
        prev_param3 = self.param3_dropdown.currentText()
        prev_param4 = self.param4_dropdown.currentText()
        # Show/hide and configure param3 widgets
        if param3_is_lineedit:
            self.param3_dropdown.hide()
            self.param3_lineedit.show()
            self.param3_lineedit.setPlaceholderText(param3_name)
            self.param3_lineedit.setText("")
        else:
            self.param3_lineedit.hide()
            self.param3_dropdown.show()
            self.param3_dropdown.blockSignals(True)
            self.param3_dropdown.clear()
            self.param3_dropdown.addItem(param3_name + "...")
            for opt in param3_options:
                self.param3_dropdown.addItem(opt)
            self.param3_dropdown.setEnabled(has_param3)
            if prev_param3 in param3_options:
                self.param3_dropdown.setCurrentText(prev_param3)
            self.param3_dropdown.blockSignals(False)
        # Show/hide and configure param4 widgets
        if param4_is_lineedit:
            self.param4_dropdown.hide()
            self.param4_lineedit.show()
            self.param4_lineedit.setPlaceholderText(param4_name)
            self.param4_lineedit.setText("")
        else:
            self.param4_lineedit.hide()
            self.param4_dropdown.show()
            self.param4_dropdown.blockSignals(True)
            self.param4_dropdown.clear()
            self.param4_dropdown.addItem(param4_name + "...")
            for opt in param4_options:
                self.param4_dropdown.addItem(opt)
            self.param4_dropdown.setEnabled(has_param4)
            if prev_param4 in param4_options:
                self.param4_dropdown.setCurrentText(prev_param4)
            self.param4_dropdown.blockSignals(False)
        self.update_assembled_message()

    def update_assembled_message(self, *_):
        cmd = self.command_dropdown.currentText()
        # Get command info and parameters
        param_defs = []
        if self._command_dict:
            cmd_info = self._command_dict.get('commands', {}).get(cmd, {})
            param_defs = cmd_info.get('parameters', [])
        # Find max param_number to size the list (param_number is 1-based, 1=instance)
        # Debug print removed: param_defs loading
        max_param_num = 1
        for p in param_defs:
            if isinstance(p.get('param_number'), int):
                max_param_num = max(max_param_num, p['param_number'])
        # Build param_values: index 0 is instance, rest are from dropdowns by param_number
        param_values = [""] * max_param_num
        # Fill param_values using param_dropdown_map
        # Ensure param_dropdown_map is always available
        if not hasattr(self, 'param_dropdown_map') or not isinstance(self.param_dropdown_map, dict):
            self.param_dropdown_map = {1: self.instance_dropdown}
        # Only process the first matching parameter definition for each param_number
        from PySide6.QtWidgets import QLineEdit, QComboBox
        processed_param_numbers = set()
        for p in param_defs:
            pnum = p.get('param_number')
            if pnum in processed_param_numbers:
                continue
            if not isinstance(pnum, int) or pnum < 1:
                continue
            val = ""
            # Simplified: always use 1-based index for param_number==1 (instance)
            if p.get('param_number') == 1:
                idx = self.instance_dropdown.currentIndex()
                if idx > 0:
                    val = str(idx)
                    print(f"[DEBUG] Instance selected index for param 1: {val}")
                else:
                    val = ""
            elif p.get('name', '').lower() == 'mode':
                v = self.mode_dropdown.currentText()
                if not v.endswith("...") and v:
                    val = v
                else:
                    val = ""
            elif p.get('type') == 'boolean':
                # Use dropdown or lineedit for boolean
                widget = self.param_dropdown_map.get(pnum)
                if isinstance(widget, QComboBox) and widget.isEnabled() and widget.count() > 1:
                    v = widget.currentText()
                    v_lower = v.lower()
                    if v_lower in ("on", "1", "true"):
                        val = "1"
                    elif v_lower in ("off", "0", "false"):
                        val = "0"
                    else:
                        val = ""
                elif isinstance(widget, QLineEdit) and widget.isVisible():
                    v = widget.text().strip().lower()
                    if v in ("on", "1", "true"):
                        val = "1"
                    elif v in ("off", "0", "false"):
                        val = "0"
                    else:
                        val = ""
            else:
                widget = self.param_dropdown_map.get(pnum)
                if isinstance(widget, QComboBox) and widget.isEnabled() and widget.count() > 1:
                    v = widget.currentText()
                    if not v.endswith("..."):
                        val = v
                elif isinstance(widget, QLineEdit) and widget.isVisible():
                    val = widget.text().strip()
            param_values[pnum-1] = val
            processed_param_numbers.add(pnum)
        # Use param_count from command dictionary to determine required fields
        param_count = 0
        if self._command_dict:
            cmd_info = self._command_dict.get('commands', {}).get(cmd, {})
            param_count = cmd_info.get('param_count', 0)
        # Compose message: command + only parameters that are enabled and present for the selected mode
        msg_parts = [cmd]
        from PySide6.QtWidgets import QLineEdit, QComboBox
        for pnum, widget in self.param_dropdown_map.items():
            val = ""
            if pnum == 1:
                idx = widget.currentIndex()
                if idx > 0:
                    val = str(idx)
            elif pnum == 2:
                v = widget.currentText()
                if not v.endswith("...") and v:
                    val = v
            elif isinstance(widget, QLineEdit) and widget.isVisible():
                val = widget.text().strip()
            elif isinstance(widget, QComboBox) and widget.isVisible():
                if widget.isEnabled() and widget.count() > 1:
                    v = widget.currentText()
                    # Find the parameter definition for this pnum
                    pdef = None
                    if self._command_dict:
                        cmd_info = self._command_dict.get('commands', {}).get(cmd, {})
                        for pd in cmd_info.get('parameters', []):
                            if pd.get('param_number') == pnum:
                                conds = pd.get('condition', [])
                                if isinstance(conds, str):
                                    conds = [conds]
                                mode_val = self.mode_dropdown.currentText() if self.mode_dropdown.count() > 1 else None
                                if not conds or any(f"mode == {mode_val}" == cond.strip() for cond in conds):
                                    pdef = pd
                                    break
                    if not v.endswith("...") and v != "":
                        if pdef and (pdef.get('type') == 'boolean' or pdef.get('type') == 'enum'):
                            v_lower = v.lower()
                            val = "1" if v_lower in ("on", "1", "true") else "0"
                        else:
                            val = v
            if val != "":
                print(f"[DEBUG] Param {pnum} value for message: {val}")
                msg_parts.append(val)
        # Debug prints removed
        # Only show if all required fields are filled
        if all(part != "" for part in msg_parts):
            msg = ",".join(msg_parts)
            self.assembled_output.setText(msg)
        else:
            self.assembled_output.setText("")

    def send_udp_message(self):
        # Emit the assembled message via signal for MainWindow to handle actual sending
        msg = self.assembled_output.text()
        self.send_message_signal.emit(msg)
        self.response_box.setText(f"[UI] Sent: {msg}")
    def __init__(self, command_dict, command_config):
        super().__init__()
        self._command_dict = command_dict
        self._command_config = command_config
        self.command_dropdown = QComboBox()
        self.instance_dropdown = QComboBox()
        self.mode_dropdown = QComboBox()
        self.param3_dropdown = QComboBox()
        self.param4_dropdown = QComboBox()
        self.param3_lineedit = QLineEdit()
        self.param4_lineedit = QLineEdit()
        self.param3_lineedit.setPlaceholderText("Parameter 3 value...")
        self.param4_lineedit.setPlaceholderText("Parameter 4 value...")
        self.param3_lineedit.hide()
        self.param4_lineedit.hide()
        self.command_dropdown.addItem("Command...")
        self.instance_dropdown.addItem("Instance...")
        self.mode_dropdown.addItem("Mode...")
        self.param3_dropdown.addItem("Parameter 3...")
        self.param4_dropdown.addItem("Parameter 4...")
        self.instance_dropdown.setEnabled(False)
        self.mode_dropdown.setEnabled(False)
        self.param3_dropdown.setEnabled(False)
        self.param4_dropdown.setEnabled(False)
        selectors_layout = QHBoxLayout()
        selectors_layout.setSpacing(8)
        selectors_layout.setContentsMargins(0, 0, 0, 0)
        selectors_layout.addWidget(QLabel("Command:"))
        selectors_layout.addWidget(self.command_dropdown)
        selectors_layout.addWidget(QLabel("Instance:"))
        selectors_layout.addWidget(self.instance_dropdown)
        selectors_layout.addWidget(QLabel("Mode:"))
        selectors_layout.addWidget(self.mode_dropdown)
        selectors_layout.addWidget(QLabel("Parameter 3:"))
        selectors_layout.addWidget(self.param3_dropdown)
        selectors_layout.addWidget(self.param3_lineedit)
        selectors_layout.addWidget(QLabel("Parameter 4:"))
        selectors_layout.addWidget(self.param4_dropdown)
        selectors_layout.addWidget(self.param4_lineedit)
        self.assembled_label = QLabel("Message:")
        self.assembled_output = QLabel("")
        self.assembled_output.setMinimumWidth(200)
        self.assembled_output.setFixedHeight(25)
        self.assembled_output.setStyleSheet("background: #f0f0f0; border: 1px solid #ccc; padding: 4px;")
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        self.response_box.setFixedSize(400, 60)
        self.response_box.setStyleSheet("background: #fffbe6; border: 1px solid #ccc; padding: 4px;")
        self.send_button = QPushButton("Send UDP Message")
        self.send_button.setFixedSize(60, 60)
        self.send_button.setText('SEND')
        self.send_button.setSizePolicy(self.send_button.sizePolicy().horizontalPolicy(), self.send_button.sizePolicy().verticalPolicy())
        output_row_layout = QHBoxLayout()
        output_row_layout.setSpacing(8)
        output_row_layout.setContentsMargins(0, 0, 0, 0)
        output_row_layout.addWidget(self.assembled_label)
        output_row_layout.addWidget(self.assembled_output)
        output_row_layout.addWidget(self.response_box)
        output_row_layout.addStretch(1)
        output_row_layout.addWidget(self.send_button)
        msg_layout = QVBoxLayout()
        msg_layout.setSpacing(8)
        msg_layout.setContentsMargins(0, 0, 0, 0)
        msg_layout.addLayout(selectors_layout)
        msg_layout.addLayout(output_row_layout)
        msg_layout.addStretch(1)
        self.setLayout(msg_layout)
        # Ensure dropdowns are populated and signals connected
        self.setup_logic()
