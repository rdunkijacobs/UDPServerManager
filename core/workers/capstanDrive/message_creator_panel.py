from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QLabel, QLineEdit, QPushButton, QMenu
from PySide6.QtCore import Signal
import config

class MessageCreatorPanel(QWidget):
    send_message_signal = Signal(str)
    user_input_changed = Signal()  # Emitted when any user input changes
    
    def __init__(self, command_dict, command_config):
        super().__init__()
        self._command_dict = command_dict
        self._command_config = command_config
        self._current_command = None  # Store selected command
        
        # Replace command dropdown with a menu button
        self.command_button = QPushButton("Select Command...")
        self.command_button.setMinimumWidth(config.DROPDOWN_WIDTH)
        self.command_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
            }
        """)
        
        self.instance_dropdown = QComboBox()
        self.instance_dropdown.setMinimumWidth(config.DROPDOWN_WIDTH)
        self.instance_dropdown.setMaxVisibleItems(13)
        
        # Create 10 parameter rows (labels, dropdowns, and lineedits)
        self.param_labels = []
        self.param_dropdowns = []
        self.param_lineedits = []
        self.param_unit_labels = []  # Unit labels for each parameter
        
        for i in range(10):
            label = QLabel(f"Parameter {i+1}:")
            label.setFixedWidth(config.LABEL_WIDTH)
            dropdown = QComboBox()
            dropdown.setMinimumWidth(config.DROPDOWN_WIDTH)
            dropdown.setMaxVisibleItems(13)
            lineedit = QLineEdit()
            lineedit.setMinimumWidth(config.DROPDOWN_WIDTH)
            lineedit.setPlaceholderText(f"Enter value...")
            unit_label = QLabel("")
            unit_label.setFixedWidth(60)  # Fixed width for units
            
            # Initially hide all parameter widgets
            label.hide()
            dropdown.hide()
            lineedit.hide()
            unit_label.hide()
            
            self.param_labels.append(label)
            self.param_dropdowns.append(dropdown)
            self.param_lineedits.append(lineedit)
            self.param_unit_labels.append(unit_label)
        
        self.instance_dropdown.addItem("Instance...")
        self.instance_dropdown.setEnabled(False)
        
        # Build layout - all aligned to the left
        msg_layout = QVBoxLayout()
        msg_layout.setSpacing(config.VERTICAL_SPACING)
        msg_layout.setContentsMargins(0, 0, 0, 0)
        
        # Command row
        cmd_layout = QHBoxLayout()
        cmd_layout.setSpacing(config.HORIZONTAL_SPACING)
        cmd_label = QLabel("Command:")
        cmd_label.setFixedWidth(config.LABEL_WIDTH)
        cmd_layout.addWidget(cmd_label)
        cmd_layout.addWidget(self.command_button)
        cmd_layout.addStretch(1)
        msg_layout.addLayout(cmd_layout)
        
        # Instance row (label will be updated dynamically)
        inst_layout = QHBoxLayout()
        inst_layout.setSpacing(config.HORIZONTAL_SPACING)
        self.instance_label = QLabel("Instance:")
        self.instance_label.setFixedWidth(config.LABEL_WIDTH)
        inst_layout.addWidget(self.instance_label)
        inst_layout.addWidget(self.instance_dropdown)
        inst_layout.addStretch(1)
        msg_layout.addLayout(inst_layout)
        
        # Parameter rows (10 total)
        for i in range(10):
            param_layout = QHBoxLayout()
            param_layout.setSpacing(config.HORIZONTAL_SPACING)
            param_layout.addWidget(self.param_labels[i])
            param_layout.addWidget(self.param_dropdowns[i])
            param_layout.addWidget(self.param_lineedits[i])
            param_layout.addWidget(self.param_unit_labels[i])  # Add unit label
            param_layout.addStretch(1)
            msg_layout.addLayout(param_layout)
        
        # Message output
        self.assembled_label = QLabel("Message:")
        self.assembled_label.setFixedWidth(config.LABEL_WIDTH)
        self.assembled_output = QLabel("")
        self.assembled_output.setMinimumWidth(config.MESSAGE_OUTPUT_MIN_WIDTH)
        self.assembled_output.setFixedHeight(config.MESSAGE_OUTPUT_HEIGHT)
        self.assembled_output.setStyleSheet("background: #f0f0f0; border: 1px solid #ccc; padding: 4px;")
        
        output_row_layout = QHBoxLayout()
        output_row_layout.setSpacing(8)
        output_row_layout.addWidget(self.assembled_label)
        output_row_layout.addWidget(self.assembled_output)
        output_row_layout.addStretch(1)
        
        msg_layout.addLayout(output_row_layout)
        msg_layout.addStretch(1)
        
        self.setLayout(msg_layout)
        # Populate dropdowns and connect signals
        self.setup_logic()

    def set_server(self, server):
        """
        Set the current server context for the message creator panel.
        Stores the server dictionary and resets fields if needed.
        """
        self._current_server = server
        self.clear_fields()

    def clear_fields(self):
        """
        Clear or reset all user-editable fields in the panel.
        """
        self._current_command = None
        self.command_button.setText("Select Command...")
        self.instance_dropdown.setCurrentIndex(0)
        self.instance_dropdown.show()
        self.instance_label.show()
        for i in range(10):
            self.param_dropdowns[i].setCurrentIndex(0)
            self.param_lineedits[i].clear()
            self.param_labels[i].hide()
            self.param_dropdowns[i].hide()
            self.param_lineedits[i].hide()
            self.param_unit_labels[i].hide()  # Hide unit labels too
        self.assembled_output.clear()

    def setup_logic(self):
        # Build command menu with categories
        self.build_command_menu()
        
        # Connect instance dropdown
        self.instance_dropdown.currentTextChanged.connect(self.update_parameters)
        self.instance_dropdown.currentTextChanged.connect(self.on_user_input_changed)
        
        # Connect all parameter dropdowns to trigger parameter refresh AND message update
        for i in range(10):
            self.param_dropdowns[i].currentTextChanged.connect(self.on_parameter_changed)
            self.param_lineedits[i].textChanged.connect(self.update_assembled_message)
            self.param_lineedits[i].textChanged.connect(self.on_user_input_changed)
    
    def build_command_menu(self):
        """Build the hierarchical command menu with categories."""
        if not self._command_dict or 'commands' not in self._command_dict:
            return
        
        menu = QMenu(self)
        commands = self._command_dict['commands']
        
        # Group commands by category
        categories = {}
        for cmd_name, cmd_info in commands.items():
            category = cmd_info.get('category', 'Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd_name)
        
        # Sort categories to ensure consistent order
        category_order = [
            "Device Control",
            "Device Status", 
            "Error Handling",
            "System Administration"
        ]
        
        # Create submenu for each category
        for category in category_order:
            if category in categories:
                submenu = menu.addMenu(category)
                # Sort commands within category alphabetically
                for cmd_name in sorted(categories[category]):
                    action = submenu.addAction(cmd_name)
                    action.triggered.connect(lambda checked=False, cmd=cmd_name: self.on_command_selected(cmd))
        
        # Add any uncategorized commands at the bottom
        if 'Uncategorized' in categories:
            menu.addSeparator()
            for cmd_name in sorted(categories['Uncategorized']):
                action = menu.addAction(cmd_name)
                action.triggered.connect(lambda checked=False, cmd=cmd_name: self.on_command_selected(cmd))
        
        self.command_button.setMenu(menu)
    
    def on_command_selected(self, command):
        """Called when a command is selected from the menu."""
        self._current_command = command
        self.command_button.setText(command)
        self.update_command_related_dropdowns(command)
        self.on_user_input_changed()
    
    def on_parameter_changed(self):
        """Called when any parameter dropdown changes - refresh parameters and update message."""
        self.update_parameters()
        self.update_assembled_message()
        self.user_input_changed.emit()
    
    def on_user_input_changed(self):
        """Called when any user input changes - emit signal to notify parent."""
        self.user_input_changed.emit()

    def update_command_related_dropdowns(self, command):
        # Clear instance dropdown
        self.instance_dropdown.blockSignals(True)
        self.instance_dropdown.clear()
        self.instance_dropdown.addItem("Instance...")
        
        # Hide all parameter widgets
        for i in range(10):
            self.param_labels[i].hide()
            self.param_dropdowns[i].hide()
            self.param_lineedits[i].hide()
            self.param_unit_labels[i].hide()  # Hide unit labels
        
        if not command or command == "Select Command...":
            self.instance_dropdown.setEnabled(False)
            self.instance_label.setText("Instance:")
            self.instance_dropdown.blockSignals(False)
            return
        
        # Check if parameter 1 is an enum type
        param1_is_enum = False
        if self._command_dict:
            cmd_info = self._command_dict.get('commands', {}).get(command, {})
            params = cmd_info.get('parameters', [])
            for p in params:
                if p.get('param_number') == 1:
                    param_name = p.get('name', 'Instance')
                    self.instance_label.setText(f"{param_name}:")
                    if p.get('type') == 'enum':
                        param1_is_enum = True
                    break
        
        # If param 1 is enum, hide instance dropdown and show it as regular parameter
        if param1_is_enum:
            self.instance_dropdown.hide()
            self.instance_label.hide()
            self.instance_dropdown.setEnabled(False)
            self.instance_dropdown.blockSignals(False)
        else:
            # Populate instance dropdown from config (old behavior)
            self.instance_dropdown.show()
            self.instance_label.show()
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
        
        # Update parameters for this command
        self.update_parameters()

    def update_parameters(self, *_):
        """Update all parameter widgets based on the selected command and instance."""
        command = self._current_command
        instance = self.instance_dropdown.currentText()
        
        if not command or command == "Select Command...":
            # Hide all parameters
            for i in range(10):
                self.param_labels[i].hide()
                self.param_dropdowns[i].hide()
                self.param_lineedits[i].hide()
                self.param_unit_labels[i].hide()  # Hide unit labels
            return
        
        # Get command info from dictionary
        if not self._command_dict:
            return
        
        cmd_info = self._command_dict.get('commands', {}).get(command, {})
        params = cmd_info.get('parameters', [])
        
        # Check if parameter 1 is an enum
        param1_is_enum = False
        for p in params:
            if p.get('param_number') == 1 and p.get('type') == 'enum':
                param1_is_enum = True
                break
        
        # Build a map of param_number to current dropdown values (for condition checking)
        current_values = {}
        for p in params:
            param_num = p.get('param_number', 1)
            # Determine the index based on whether param 1 is enum
            if param1_is_enum:
                if param_num >= 1 and param_num <= 8:
                    idx = param_num - 1
                else:
                    continue
            else:
                if param_num >= 2 and param_num <= 8:
                    idx = param_num - 2
                else:
                    continue
            
            if self.param_dropdowns[idx].isVisible() and self.param_dropdowns[idx].count() > 1:
                val = self.param_dropdowns[idx].currentText()
                if not val.endswith("..."):
                    param_name = p.get('name', '')
                    current_values[param_name] = val
        
        # Now rebuild all parameters, checking conditions against current values
        # Track which parameters to show
        params_to_show = []
        
        for p in params:
            param_num = p.get('param_number', 1)
            # If param 1 is enum, include it; otherwise skip param 1
            if param1_is_enum:
                if param_num < 1 or param_num > 8:
                    continue
            else:
                if param_num < 2 or param_num > 8:
                    continue
            
            # Check conditions
            conditions = p.get('condition', [])
            if isinstance(conditions, str):
                conditions = [conditions]
            
            show_param = True
            if conditions:
                show_param = False
                for cond in conditions:
                    # Parse condition like "mode == blink"
                    if '==' in cond:
                        parts = cond.split('==')
                        cond_param = parts[0].strip()
                        cond_value = parts[1].strip()
                        # Check if the condition is satisfied
                        if current_values.get(cond_param) == cond_value:
                            show_param = True
                            break
            
            if show_param:
                params_to_show.append(p)
        
        # Clear and hide all parameter widgets first
        for i in range(10):
            self.param_labels[i].hide()
            self.param_dropdowns[i].blockSignals(True)
            self.param_dropdowns[i].hide()
            self.param_lineedits[i].blockSignals(True)
            self.param_lineedits[i].hide()
            self.param_unit_labels[i].hide()  # Hide unit labels
            # Store current values before clearing
            old_dropdown_val = self.param_dropdowns[i].currentText() if self.param_dropdowns[i].count() > 1 else ""
            old_lineedit_val = self.param_lineedits[i].text()
            self.param_dropdowns[i].clear()
            self.param_lineedits[i].clear()
            self.param_unit_labels[i].setText("")  # Clear unit text
            # Store for restoration
            if not hasattr(self, '_saved_values'):
                self._saved_values = {}
            self._saved_values[i] = (old_dropdown_val, old_lineedit_val)
        
        # Build widgets for parameters that should be shown
        for p in params_to_show:
            param_num = p.get('param_number', 1)
            # Determine index based on whether param 1 is enum
            if param1_is_enum:
                idx = param_num - 1  # param 1->0, param 2->1, etc.
            else:
                idx = param_num - 2  # param 2->0, param 3->1, etc.
            
            param_name = p.get('name', f'Parameter {param_num}')
            param_type = p.get('type', 'string')
            param_units = p.get('units', '')  # Get units from parameter
            
            # Set label
            self.param_labels[idx].setText(f"{param_name}:")
            self.param_labels[idx].show()
            
            # Set unit label if units exist
            if param_units:
                self.param_unit_labels[idx].setText(param_units)
                self.param_unit_labels[idx].show()
            else:
                self.param_unit_labels[idx].setText("")
                self.param_unit_labels[idx].hide()
            
            # Configure widget based on type
            if param_type == 'enum':
                dropdown = self.param_dropdowns[idx]
                dropdown.addItem(f"{param_name}...")
                for opt in p.get('options', []):
                    dropdown.addItem(opt)
                # Restore previous value if it exists
                if idx in self._saved_values and self._saved_values[idx][0]:
                    old_val = self._saved_values[idx][0]
                    if not old_val.endswith("..."):
                        for i in range(dropdown.count()):
                            if dropdown.itemText(i) == old_val:
                                dropdown.setCurrentIndex(i)
                                break
                dropdown.show()
                dropdown.blockSignals(False)
            elif param_type == 'boolean':
                dropdown = self.param_dropdowns[idx]
                dropdown.addItem(f"{param_name}...")
                # Get boolean display options from parameter definition or config
                param_options = p.get('options', [])
                if param_options and len(param_options) >= 2:
                    # Use options from command dictionary [true_option, false_option]
                    display_opts = param_options[:2]
                else:
                    # Get default from config
                    bool_config = getattr(self._command_config, 'BOOLEAN_CONFIG', None)
                    if bool_config and 'display_options' in bool_config:
                        # Use first tuple from config as default
                        display_tuples = bool_config['display_options']
                        if display_tuples and len(display_tuples) > 0:
                            display_opts = list(display_tuples[0])
                        else:
                            display_opts = ['True', 'False']
                    else:
                        display_opts = ['True', 'False']
                for opt in display_opts:
                    dropdown.addItem(opt)
                # Restore previous value
                if idx in self._saved_values and self._saved_values[idx][0]:
                    old_val = self._saved_values[idx][0]
                    for i in range(dropdown.count()):
                        if dropdown.itemText(i) == old_val:
                            dropdown.setCurrentIndex(i)
                            break
                dropdown.show()
                dropdown.blockSignals(False)
            elif param_type in ('integer', 'float'):
                lineedit = self.param_lineedits[idx]
                range_info = p.get('range', {})
                if range_info:
                    min_val = range_info.get('min', '')
                    max_val = range_info.get('max', '')
                    lineedit.setPlaceholderText(f"{min_val} to {max_val}")
                else:
                    lineedit.setPlaceholderText(f"Enter {param_type}...")
                # Restore previous value
                if idx in self._saved_values and self._saved_values[idx][1]:
                    lineedit.setText(self._saved_values[idx][1])
                lineedit.show()
                lineedit.blockSignals(False)
            else:
                lineedit = self.param_lineedits[idx]
                lineedit.setPlaceholderText(f"Enter {param_name}...")
                if idx in self._saved_values and self._saved_values[idx][1]:
                    lineedit.setText(self._saved_values[idx][1])
                lineedit.show()
                lineedit.blockSignals(False)
        
        # Unblock signals for hidden widgets
        for i in range(10):
            if not self.param_labels[i].isVisible():
                self.param_dropdowns[i].blockSignals(False)
                self.param_lineedits[i].blockSignals(False)
        
        self.update_assembled_message()
        
        # Unblock signals for widgets we didn't configure
        for i in range(10):
            if not self.param_labels[i].isVisible():
                self.param_dropdowns[i].blockSignals(False)
                self.param_lineedits[i].blockSignals(False)
        
        self.update_assembled_message()

    def update_assembled_message(self, *_):
        """Assemble the message from command, instance, and parameter values."""
        cmd = self._current_command
        
        if not cmd or cmd == "Select Command...":
            self.assembled_output.setText("")
            return
        
        # Start with command
        msg_parts = [cmd]
        
        # Get parameter definitions
        if not self._command_dict:
            self.assembled_output.setText("")
            return
        
        cmd_info = self._command_dict.get('commands', {}).get(cmd, {})
        params = cmd_info.get('parameters', [])
        
        # Check if parameter 1 is an enum
        param1_is_enum = False
        for p in params:
            if p.get('param_number') == 1 and p.get('type') == 'enum':
                param1_is_enum = True
                break
        
        # Handle param 1 based on type
        if param1_is_enum:
            # Param 1 is shown as regular parameter - skip instance dropdown
            pass
        else:
            # Add instance (param 1) from instance dropdown
            instance_idx = self.instance_dropdown.currentIndex()
            if instance_idx > 0:
                msg_parts.append(str(instance_idx))
            elif self.instance_dropdown.isEnabled() and self.instance_dropdown.count() > 1:
                # Instance required but not selected
                self.assembled_output.setText("")
                return
        
        # Collect values for parameters
        param_values = {}
        for p in params:
            param_num = p.get('param_number', 1)
            
            # Determine valid range and index based on param1 type
            if param1_is_enum:
                if param_num < 1 or param_num > 8:
                    continue
                idx = param_num - 1  # param 1->0, param 2->1, etc.
            else:
                if param_num < 2 or param_num > 8:
                    continue
                idx = param_num - 2  # param 2->0, param 3->1, etc.
            
            param_type = p.get('type', 'string')
            val = ""
            
            # Get value from appropriate widget
            if self.param_dropdowns[idx].isVisible():
                dropdown_val = self.param_dropdowns[idx].currentText()
                param_name = p.get('name', '')
                if not dropdown_val.endswith("...") and dropdown_val:
                    if param_type == 'boolean':
                        # Use boolean configuration for encoding
                        bool_config = getattr(self._command_config, 'BOOLEAN_CONFIG', None)
                        if bool_config:
                            true_strings = [s.lower() for s in bool_config.get('true_strings', ['true', '1'])]
                            message_encoding = bool_config.get('message_encoding', ['1', '0'])
                            # Check if the selected value is considered true
                            is_true = dropdown_val.lower() in true_strings
                            val = message_encoding[0] if is_true else message_encoding[1]
                        else:
                            # Fallback to default behavior
                            val = "1" if dropdown_val.lower() in ("true", "1", "on") else "0"
                    elif param_type == 'enum' and param_num == 1:
                        # For parameter 1 enum, use index instead of text
                        # currentIndex() - 1 because index 0 is the placeholder ("led_number...")
                        enum_idx = self.param_dropdowns[idx].currentIndex() - 1
                        val = str(enum_idx)
                    else:
                        val = dropdown_val
            elif self.param_lineedits[idx].isVisible():
                val = self.param_lineedits[idx].text().strip()
            
            if val:
                param_values[param_num] = val
        
        # Add parameters in order (starting from 1 if enum, or 2 if integer)
        start_param = 1 if param1_is_enum else 2
        for param_num in range(start_param, 9):
            if param_num in param_values:
                msg_parts.append(param_values[param_num])
        
        # Assemble final message
        if len(msg_parts) > 1:
            msg = ",".join(msg_parts)
            self.assembled_output.setText(msg)
        else:
            self.assembled_output.setText("")

