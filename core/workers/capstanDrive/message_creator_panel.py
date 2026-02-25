from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QLabel, QLineEdit, QPushButton, QMenu, QMessageBox
from PySide6.QtCore import Signal, Qt, QTimer
from decimal import Decimal
import config
import re

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
        self._set_message_output_style('empty')

    def _format_number_no_scientific(self, numeric_str, multiplier):
        """
        Format a numeric value with multiplier without scientific notation.
        Preserves significant figures from the input string.
        
        Args:
            numeric_str: String representation of the number
            multiplier: Numeric multiplier to apply
            
        Returns:
            str: Formatted number without scientific notation
        """
        # Use Decimal for precise arithmetic
        d_value = Decimal(numeric_str.replace(',', ''))
        d_multiplier = Decimal(str(multiplier))
        result = d_value * d_multiplier
        
        # Format without scientific notation
        formatted = format(result, 'f')
        
        # Remove trailing zeros after decimal point
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        
        return formatted

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
            # Validate numeric fields when user finishes editing (moves away or presses Enter)
            self.param_lineedits[i].editingFinished.connect(lambda idx=i: self.on_field_editing_finished(idx))
    
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
    
    def on_field_editing_finished(self, idx):
        """Called when user finishes editing a line edit field (focus lost or Enter pressed)."""
        # Get the field widget
        field_widget = self.param_lineedits[idx]
        val = field_widget.text().strip()
        
        if not val or not field_widget.isVisible():
            return  # Empty or hidden field, nothing to validate
        
        # Find the parameter definition for this field
        cmd = self._current_command
        if not cmd or cmd == "Select Command..." or not self._command_dict:
            return
        
        cmd_info = self._command_dict.get('commands', {}).get(cmd, {})
        params = cmd_info.get('parameters', [])
        
        # Check if parameter 1 is an enum
        param1_is_enum = False
        for p in params:
            if p.get('param_number') == 1 and p.get('type') == 'enum':
                param1_is_enum = True
                break
        
        # Determine parameter number from index
        if param1_is_enum:
            param_num = idx + 1
        else:
            param_num = idx + 2
        
        # Find the parameter definition with this param_number and matching conditions
        # Build current values for condition checking
        current_values = {}
        for p in params:
            pnum = p.get('param_number', 1)
            pname = p.get('name', '')
            
            if param1_is_enum:
                if pnum < 1 or pnum > 8:
                    continue
                pidx = pnum - 1
            else:
                if pnum < 2 or pnum > 8:
                    continue
                pidx = pnum - 2
            
            if self.param_dropdowns[pidx].isVisible():
                dropdown_val = self.param_dropdowns[pidx].currentText()
                if dropdown_val and not dropdown_val.endswith("..."):
                    current_values[pname] = dropdown_val
            elif self.param_lineedits[pidx].isVisible():
                lineedit_val = self.param_lineedits[pidx].text().strip()
                if lineedit_val:
                    current_values[pname] = lineedit_val
        
        # Find the relevant parameter definition
        param_type = None
        param_name = None
        for p in params:
            if p.get('param_number') != param_num:
                continue
            
            # Check if this parameter's conditions are met
            conditions = p.get('condition', [])
            if isinstance(conditions, str):
                conditions = [conditions]
            
            show_param = True
            if conditions:
                show_param = False
                for cond in conditions:
                    if '==' in cond:
                        parts = cond.split('==')
                        cond_param = parts[0].strip()
                        cond_value = parts[1].strip()
                        if current_values.get(cond_param) == cond_value:
                            show_param = True
                            break
            
            if show_param:
                param_type = p.get('type', 'string')
                param_name = p.get('name', f'param{param_num}')
                param_units = p.get('units', '')
                break
        
        # Validate if it's a numeric field
        if param_type in ('float', 'integer') and param_name:
            # Check if still placeholder
            if " to " in val:
                return  # Still has placeholder, don't validate
            
            # Check for time unit suffixes and revolution/degree multipliers
            # Strip them for validation (conversion will happen during message assembly)
            val_to_validate = val
            has_suffix = False
            
            # Check if this is a time parameter
            is_time_param = False
            if isinstance(param_units, str) and param_units == 's':
                is_time_param = True
            elif isinstance(param_units, list):
                for unit_dict in param_units:
                    if isinstance(unit_dict, dict) and 's' in unit_dict.values():
                        is_time_param = True
                        break
            
            if is_time_param:
                val_lower = val.lower()
                if val_lower.endswith('ns'):
                    val_to_validate = val[:-2].strip()
                    has_suffix = True
                elif val_lower.endswith('us'):
                    val_to_validate = val[:-2].strip()
                    has_suffix = True
                elif val_lower.endswith('ms'):
                    val_to_validate = val[:-2].strip()
                    has_suffix = True
            
            # Check if this is a revolution/degree parameter
            is_rev_deg_param = False
            if isinstance(param_units, str):
                units_lower = param_units.lower()
                if 'rev' in units_lower or 'deg' in units_lower:
                    is_rev_deg_param = True
            elif isinstance(param_units, list):
                for unit_dict in param_units:
                    if isinstance(unit_dict, dict):
                        for unit_val in unit_dict.values():
                            if isinstance(unit_val, str):
                                units_lower = unit_val.lower()
                                if 'rev' in units_lower or 'deg' in units_lower:
                                    is_rev_deg_param = True
                                    break
                    if is_rev_deg_param:
                        break
            
            if is_rev_deg_param and len(val) > 1:
                # Check for k/K/m/M multiplier suffix (SI prefixes)
                # m = milli (0.001), k/K = kilo (1000), M = mega (1000000)
                last_char = val[-1]
                if last_char in ['k', 'K', 'm', 'M']:
                    # Verify the part before multiplier looks like a number
                    test_val = val[:-1].strip()
                    # Quick check: should start with digit, minus, or decimal point
                    if test_val and (test_val[0].isdigit() or test_val[0] in ['-', '.']):
                        val_to_validate = test_val
                        has_suffix = True
            
            # Apply leading zero fix to the value being validated
            if val_to_validate.startswith('.'):
                val_to_validate = '0' + val_to_validate
                if not has_suffix:
                    field_widget.setText(val_to_validate)
            elif val_to_validate.startswith('-.'):
                val_to_validate = '-0.' + val_to_validate[2:]
                if not has_suffix:
                    field_widget.setText(val_to_validate)
            
            # Validate the numeric value (without time suffix)
            if not self._validate_numeric_input(val_to_validate, param_type, param_name):
                self._flash_invalid_field(field_widget, param_name, param_type, param_units)
    
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
                # Handle context-dependent units (list of dicts)
                if isinstance(param_units, list):
                    # Units depend on another parameter's value
                    # Example: [{"time": "s"}, {"revolutions": "rev"}]
                    # Keys match possible values of another parameter
                    unit_str = ""
                    for unit_dict in param_units:
                        if isinstance(unit_dict, dict):
                            for context_value, unit in unit_dict.items():
                                # Check if this context value appears in current_values
                                if context_value in current_values.values():
                                    unit_str = unit
                                    break
                        if unit_str:
                            break
                    # If we couldn't determine, show first available unit as default
                    if not unit_str and param_units:
                        first_dict = param_units[0] if param_units else {}
                        if isinstance(first_dict, dict):
                            unit_str = list(first_dict.values())[0] if first_dict else ""
                    self.param_unit_labels[idx].setText(unit_str)
                    self.param_unit_labels[idx].show()
                else:
                    # Normal string units
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
                    if isinstance(opt, dict):
                        # New format with tooltip: {"value": "tC", "tooltip": "..."}
                        value = opt.get('value', '')
                        tooltip = opt.get('tooltip', '')
                        dropdown.addItem(value)
                        if tooltip:
                            dropdown.setItemData(dropdown.count() - 1, tooltip, Qt.ToolTipRole)
                    else:
                        # Simple string format (backward compatible)
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

    def _set_message_output_style(self, state):
        """
        Set the background color of the assembled message output.
        
        Args:
            state: 'empty' (gray), 'incomplete' (pale yellow), 'complete' (light green)
        """
        if state == 'empty':
            bg_color = "#f0f0f0"  # Gray - no command selected
        elif state == 'incomplete':
            bg_color = "#ffffcc"  # Pale yellow - missing required parameters
        elif state == 'complete':
            bg_color = "#ccffcc"  # Light green - all required parameters present
        else:
            bg_color = "#f0f0f0"  # Default to gray
        
        self.assembled_output.setStyleSheet(f"background: {bg_color}; border: 1px solid #ccc; padding: 4px;")

    def update_assembled_message(self, *_):
        """Assemble the message from command, instance, and parameter values."""
        cmd = self._current_command
        
        if not cmd or cmd == "Select Command...":
            self.assembled_output.setText("")
            self._set_message_output_style('empty')
            return
        
        # Start with command
        msg_parts = [cmd]
        
        # Get parameter definitions
        if not self._command_dict:
            self.assembled_output.setText("")
            self._set_message_output_style('empty')
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
                self._set_message_output_style('incomplete')
                return
        
        # Collect values for parameters
        param_values = {}
        
        # Build a map of current parameter values for condition checking
        current_values = {}
        for p in params:
            param_num = p.get('param_number', 1)
            param_name = p.get('name', '')
            
            if param1_is_enum:
                if param_num < 1 or param_num > 8:
                    continue
                idx = param_num - 1
            else:
                if param_num < 2 or param_num > 8:
                    continue
                idx = param_num - 2
            
            # Get current value from widget (for condition checking)
            if self.param_dropdowns[idx].isVisible():
                dropdown_val = self.param_dropdowns[idx].currentText()
                if dropdown_val and not dropdown_val.endswith("..."):
                    current_values[param_name] = dropdown_val
            elif self.param_lineedits[idx].isVisible():
                lineedit_val = self.param_lineedits[idx].text().strip()
                if lineedit_val:
                    current_values[param_name] = lineedit_val
        
        # Now collect parameter values, checking conditions
        for p in params:
            param_num = p.get('param_number', 1)
            param_name = p.get('name', '')
            param_type = p.get('type', 'string')
            
            # Skip if we've already processed a parameter with this param_number
            # (multiple conditional parameters can share the same param_number)
            if param_num in param_values:
                continue
            
            # Check if parameter's conditions are met
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
            
            # Skip this parameter if its conditions aren't met
            if not show_param:
                continue
            
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
                        # For parameter 1 enum, use index instead of text.
                        # Index 0 is the placeholder ("led_number..."), so currentIndex()
                        # already gives the correct 1-based index for the selected option.
                        enum_idx = self.param_dropdowns[idx].currentIndex()
                        val = str(enum_idx)
                    else:
                        val = dropdown_val
            elif self.param_lineedits[idx].isVisible():
                val = self.param_lineedits[idx].text().strip()
                
                # Check if value is still a placeholder (contains " to " for range fields)
                if val and " to " in val:
                    # Verify it matches the expected placeholder pattern
                    param_range = p.get('range', {})
                    if param_range:
                        min_val = param_range.get('min')
                        max_val = param_range.get('max')
                        expected_placeholder = f"{min_val} to {max_val}"
                        if val == expected_placeholder:
                            # Still has placeholder text - treat as empty
                            val = ""
                
                # Apply leading zero fix for numeric values (validation happens on editingFinished)
                if val and param_type in ('float', 'integer'):
                    if val.startswith('.'):
                        val = '0' + val
                    elif val.startswith('-.'):
                        val = '-0.' + val[2:]
                
                # Strip commas from numeric values for message assembly
                # (commas are for display only, edge device doesn't need them)
                if val and param_type in ('float', 'integer'):
                    val = val.replace(',', '')
                
                # Handle time unit suffixes (ms, us, ns) for time-based parameters
                # System default is seconds, but users can enter with unit suffixes
                param_units = p.get('units', '')
                if val and param_type in ('float', 'integer'):
                    # Check if this is a time parameter (units in seconds)
                    # Handle both string units and list of context-dependent units
                    is_time_param = False
                    if isinstance(param_units, str) and param_units == 's':
                        is_time_param = True
                    elif isinstance(param_units, list):
                        # Check if any context has 's' as unit
                        for unit_dict in param_units:
                            if isinstance(unit_dict, dict) and 's' in unit_dict.values():
                                is_time_param = True
                                break
                    
                    if is_time_param:
                        # Check for time unit suffixes (case insensitive)
                        val_lower = val.lower()
                        multiplier = 1.0
                        suffix = ""
                        
                        if val_lower.endswith('ns'):
                            multiplier = 1e-9
                            suffix = 'ns'
                        elif val_lower.endswith('us'):
                            multiplier = 1e-6
                            suffix = 'us'
                        elif val_lower.endswith('ms'):
                            multiplier = 1e-3
                            suffix = 'ms'
                        
                        if suffix:
                            # Extract numeric part (remove suffix)
                            numeric_part = val[:-len(suffix)].strip()
                            try:
                                # Convert to seconds using Decimal for precision
                                val = self._format_number_no_scientific(numeric_part, multiplier)
                            except (ValueError, Exception):
                                # Invalid number, let validation handle it later
                                pass
                    
                    # Check if this is a revolution/degree parameter
                    is_rev_deg_param = False
                    if isinstance(param_units, str):
                        units_lower = param_units.lower()
                        if 'rev' in units_lower or 'deg' in units_lower:
                            is_rev_deg_param = True
                    elif isinstance(param_units, list):
                        for unit_dict in param_units:
                            if isinstance(unit_dict, dict):
                                for unit_val in unit_dict.values():
                                    if isinstance(unit_val, str):
                                        units_lower = unit_val.lower()
                                        if 'rev' in units_lower or 'deg' in units_lower:
                                            is_rev_deg_param = True
                                            break
                            if is_rev_deg_param:
                                break
                    
                    if is_rev_deg_param and len(val) > 1:
                        # Check for k/K/m/M multiplier suffixes (SI prefixes, case sensitive)
                        # m = milli (0.001), k/K = kilo (1000), M = mega (1000000)
                        last_char = val[-1]
                        multiplier = 1.0
                        suffix = ""
                        
                        if last_char == 'k' or last_char == 'K':
                            multiplier = 1e3  # kilo
                            suffix = last_char
                        elif last_char == 'm':
                            multiplier = 1e-3  # milli
                            suffix = last_char
                        elif last_char == 'M':
                            multiplier = 1e6  # mega
                            suffix = last_char
                        
                        if suffix:
                            # Extract numeric part (remove suffix)
                            numeric_part = val[:-1].strip()
                            try:
                                # Apply multiplier using Decimal for precision
                                val = self._format_number_no_scientific(numeric_part, multiplier)
                            except (ValueError, Exception):
                                # Invalid number, let validation handle it later
                                pass
            
            if val:
                param_values[param_num] = val
        
        # Build parameter list with placeholders for missing values
        # Track if any required parameters are missing
        all_required_present = True
        param_list = []
        
        # Determine expected parameters to display
        expected_params = []
        for p in params:
            param_num = p.get('param_number', 1)
            optional = p.get('optional', False)
            
            # Check if parameter has a valid range
            if param1_is_enum:
                if param_num < 1 or param_num > 8:
                    continue
                idx = param_num - 1
            else:
                if param_num < 2 or param_num > 8:
                    continue
                idx = param_num - 2
            
            # Check if widget is visible (parameter is relevant for current configuration)
            if (self.param_dropdowns[idx].isVisible() or self.param_lineedits[idx].isVisible()):
                expected_params.append({
                    'num': param_num,
                    'optional': optional,
                    'name': p.get('name', f'param{param_num}')
                })
        
        # Sort by parameter number
        expected_params.sort(key=lambda x: x['num'])
        
        # Build parameter list with values or placeholders (only once per parameter)
        start_param = 1 if param1_is_enum else 2
        added_params = set()  # Track which parameters we've already added
        
        for ep in expected_params:
            param_num = ep['num']
            if param_num >= start_param and param_num not in added_params:
                added_params.add(param_num)  # Mark as added
                if param_num in param_values:
                    param_list.append(param_values[param_num])
                else:
                    # Missing parameter - add single box placeholder
                    param_list.append("□")
                    if not ep['optional']:
                        all_required_present = False
        
        # Assemble final message
        # If param_count == 0, only the command is needed
        if len(expected_params) == 0:
            # No parameters - just the command
            self.assembled_output.setText(msg_parts[0])
            self._set_message_output_style('complete')
        elif len(param_list) > 0:
            # Command with parameters (possibly with placeholders)
            msg_parts.extend(param_list)
            msg = ",".join(msg_parts)
            self.assembled_output.setText(msg)
            if all_required_present:
                self._set_message_output_style('complete')
            else:
                self._set_message_output_style('incomplete')
        else:
            self.assembled_output.setText(msg_parts[0])
            self._set_message_output_style('incomplete')

    def _validate_numeric_input(self, value, param_type, param_name):
        """
        Validate that a string represents a valid number.
        Supports integers, floats, scientific notation, and properly-placed commas.
        
        Args:
            value: String to validate
            param_type: 'integer' or 'float'
            param_name: Name of parameter for error messages
            
        Returns:
            True if valid, False otherwise
        """
        if not value:
            return True  # Empty is handled elsewhere
        
        # First validate comma placement if commas are present
        if ',' in value:
            # Commas are ONLY valid in the integer part (before decimal or exponent)
            # Check if comma appears after decimal point or exponent marker
            if '.' in value:
                decimal_pos = value.find('.')
                if ',' in value[decimal_pos:]:
                    return False  # Comma after decimal point (e.g., 0.100,345)
            
            if 'e' in value.lower():
                exp_pos = value.lower().find('e')
                if ',' in value[exp_pos:]:
                    return False  # Comma after exponent marker (e.g., 1e3,000)
            
            # Split on decimal point and exponent marker to get integer part
            parts = re.split(r'[.eE]', value, 1)
            integer_part = parts[0]
            
            # Check comma placement in integer part
            # Valid: 1,000 or 12,345 or 1,234,567
            # Invalid: ,001 or 0,001 or 1,00 or 1,2,34
            
            # Remove optional leading sign for comma checking
            check_part = integer_part.lstrip('+-')
            
            if ',' in check_part:
                # Cannot start or end with comma
                if check_part.startswith(',') or check_part.endswith(','):
                    return False
                
                # Split by commas and check grouping
                groups = check_part.split(',')
                
                # First group can be 1-3 digits, all others must be exactly 3 digits
                if len(groups[0]) > 3 or len(groups[0]) == 0:
                    return False
                
                # First group cannot be all zeros (0,001 is invalid - should be 0.001)
                if groups[0] == '0' or groups[0] == '00' or groups[0] == '000':
                    return False
                
                for group in groups[1:]:
                    if len(group) != 3:
                        return False
                    if not group.isdigit():
                        return False
        
        # Remove commas for numeric validation
        value_no_commas = value.replace(',', '')
        
        if param_type == 'integer':
            # Integer: optional sign, digits only (no decimal point)
            # Also allow scientific notation like 1e3, 1E+3, -2e-5
            pattern = r'^[+-]?(\d+([eE][+-]?\d+)?)$'
            if not re.match(pattern, value_no_commas):
                return False
            # Try to parse to verify it's actually a valid integer
            try:
                float(value_no_commas)  # Use float to handle scientific notation
                return True
            except ValueError:
                return False
                
        elif param_type == 'float':
            # Float: optional sign, digits with optional decimal point
            # Also allow scientific notation like 1.5e-3, -2.7E+5
            pattern = r'^[+-]?(\d+\.?\d*|\d*\.\d+)([eE][+-]?\d+)?$'
            if not re.match(pattern, value_no_commas):
                return False
            # Try to parse to verify it's actually valid
            try:
                float(value_no_commas)
                return True
            except ValueError:
                return False
        
        return True

    def _flash_invalid_field(self, field_widget, param_name, param_type, param_units=''):
        """
        Flash a field red to indicate invalid input and show error message.
        
        Args:
            field_widget: The QLineEdit widget to flash
            param_name: Name of the parameter
            param_type: Type of parameter ('integer' or 'float')
            param_units: Units of the parameter (e.g., 's' for seconds)
        """
        # Save original stylesheet
        original_style = field_widget.styleSheet()
        
        # Create error message
        type_desc = "whole number" if param_type == 'integer' else "decimal number"
        if param_type == 'float':
            examples = "Examples: 0.5, -3.14, 1.5e-3, 2E+5"
        else:
            examples = "Examples: 42, -17, 1e3, 5E+2"
        
        # Check if this is a time parameter
        is_time_param = False
        if isinstance(param_units, str) and param_units == 's':
            is_time_param = True
        elif isinstance(param_units, list):
            for unit_dict in param_units:
                if isinstance(unit_dict, dict) and 's' in unit_dict.values():
                    is_time_param = True
                    break
        
        # Check if this is a revolution/degree parameter
        is_rev_deg_param = False
        if isinstance(param_units, str):
            units_lower = param_units.lower()
            if 'rev' in units_lower or 'deg' in units_lower:
                is_rev_deg_param = True
        elif isinstance(param_units, list):
            for unit_dict in param_units:
                if isinstance(unit_dict, dict):
                    for unit_val in unit_dict.values():
                        if isinstance(unit_val, str):
                            units_lower = unit_val.lower()
                            if 'rev' in units_lower or 'deg' in units_lower:
                                is_rev_deg_param = True
                                break
                if is_rev_deg_param:
                    break
        
        suffix_info = ""
        if is_time_param:
            suffix_info = "\n\nTime suffixes allowed: ms, us, ns (e.g., 5ms, 2.5us, 100ns)"
        elif is_rev_deg_param:
            suffix_info = "\n\nSI multipliers allowed: m (×0.001), k/K (×1,000), M (×1,000,000)\nExamples: 10m → 0.01, 5K → 5000, 2.5M → 2500000"
        
        msg = (f"Invalid {type_desc} in '{param_name}' field.\n\n"
               f"Please enter a valid {type_desc}.\n"
               f"{examples}\n\n"
               f"Commas for thousands are allowed (e.g., 1,000)."
               f"{suffix_info}")
        
        # Show error dialog
        QMessageBox.warning(self, "Invalid Number Format", msg)
        
        # Flash the field red 3 times
        flash_count = [0]  # Use list to modify in nested function
        
        def flash():
            if flash_count[0] < 6:  # 3 flashes = 6 state changes
                if flash_count[0] % 2 == 0:
                    # Set to red
                    field_widget.setStyleSheet("QLineEdit { background-color: #ffcccc; }")
                else:
                    # Restore original
                    field_widget.setStyleSheet(original_style)
                flash_count[0] += 1
                QTimer.singleShot(200, flash)  # 200ms per state
            else:
                # Final restore
                field_widget.setStyleSheet(original_style)
                # Set focus to the invalid field so user can correct it
                field_widget.setFocus()
                field_widget.selectAll()
        
        # Start flashing
        flash()
