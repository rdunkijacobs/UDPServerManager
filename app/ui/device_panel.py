from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractScrollArea
import config

class DevicePanel(QWidget):
    from PySide6.QtCore import Signal

    server_selected = Signal(dict)  # Emits the selected server dict
    server_deselected = Signal()

    def __init__(self, servers_by_location, status_icons, parent=None):
        super().__init__(parent)
        self.servers_by_location = servers_by_location
        self.status_icons = status_icons
        self.location_selector = QComboBox()
        self.location_selector.addItems(self.servers_by_location.keys())
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(2)
        self.device_table.setHorizontalHeaderLabels(["", "Description"])
        self.device_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.device_table.setSelectionMode(QTableWidget.NoSelection)
        self.device_table.verticalHeader().setVisible(False)
        self.device_table.horizontalHeader().setStretchLastSection(True)
        self.device_table.setColumnWidth(0, 16)
        self.device_table.setColumnWidth(1, 120)
        self.device_table.horizontalHeader().setVisible(False)
        self.device_table.verticalHeader().setDefaultSectionSize(20)
        self.device_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.device_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.device_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        title_label = QLabel("Edge Servers")
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setContentsMargins(0, 0, 0, 0)
        title_label.setStyleSheet("margin-bottom:0px;padding-bottom:0px;margin-top:0px;padding-top:0px;")
        title_label.setSizePolicy(title_label.sizePolicy().horizontalPolicy(), QSizePolicy.Minimum)
        layout.addWidget(title_label)
        location_label = QLabel("Location")
        location_label.setAlignment(Qt.AlignCenter)
        location_label.setContentsMargins(0, 0, 0, 0)
        location_label.setStyleSheet("margin-bottom:0px;padding-bottom:0px;margin-top:0px;padding-top:0px;")
        location_label.setSizePolicy(location_label.sizePolicy().horizontalPolicy(), QSizePolicy.Minimum)
        layout.addWidget(location_label)
        layout.addWidget(self.location_selector)
        devices_label = QLabel("Devices")
        devices_label.setAlignment(Qt.AlignCenter)
        devices_label.setStyleSheet("margin-bottom:0px;padding-bottom:0px;margin-top:0px;padding-top:0px;")
        layout.addWidget(devices_label)
        layout.addWidget(self.device_table)
        self.setLayout(layout)
        # Set minimum width for the panel
        self.setMinimumWidth(config.DEVICE_PANEL_WIDTH)
        # Connect location dropdown to update table
        self.location_selector.currentTextChanged.connect(self._on_location_changed)
        # Populate initial table
        self._on_location_changed(self.location_selector.currentText())

    def _on_location_changed(self, location):
        self.update_table_by_location(location)
        self.enable_row_selection()

    def update_table_by_location(self, location):
        """Populate the device table for a given location string."""
        import json
        self.device_table.setRowCount(0)
        servers = self.servers_by_location.get(location, [])
        self.device_table.setRowCount(len(servers))
        servers = self.servers_by_location.get(location, [])
        for i, server in enumerate(servers):
            desc = server.get("description", server.get("name", "Unnamed server"))
            status = server.get("status", "green")
            if status not in self.status_icons:
                status = "green"
            status_item = QTableWidgetItem()
            status_item.setIcon(self.status_icons.get(status, self.status_icons["green"]))
            status_item.setToolTip(f"Status: {status}\n" + json.dumps(server, indent=2))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.device_table.setItem(i, 0, status_item)
            name_item = QTableWidgetItem(desc)
            name_item.setToolTip(json.dumps(server, indent=2))
            self.device_table.setItem(i, 1, name_item)
        # ...existing code...
        self.device_table.clearSelection()
        self.active_server_row = None
        self.device_table.repaint()
        self.device_table.show()
        self.enable_row_selection()
        # Diagnostic: print row/column contents

    def enable_row_selection(self):
        self.device_table.setSelectionMode(QTableWidget.SingleSelection)
        self.device_table.cellClicked.connect(self._handle_row_selection)

    def disable_row_selection(self):
        self.device_table.setSelectionMode(QTableWidget.NoSelection)
        try:
            self.device_table.cellClicked.disconnect(self._handle_row_selection)
        except Exception:
            pass

    def _handle_row_selection(self, row, col):
        # Remove highlight from all rows
        for r in range(self.device_table.rowCount()):
            for c in range(self.device_table.columnCount()):
                item = self.device_table.item(r, c)
                if item:
                    item.setBackground(self.device_table.palette().base())
                    font = item.font()
                    font.setBold(False)
                    item.setFont(font)
        # Highlight and bold selected row
        for c in range(self.device_table.columnCount()):
            item = self.device_table.item(row, c)
            if item:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(Qt.yellow)
        self.active_server_row = row
        # Emit signal with selected server dict
        location = self.location_selector.currentText()
        servers = self.servers_by_location.get(location, [])
        if 0 <= row < len(servers):
            self.server_selected.emit(servers[row])
        else:
            self.server_deselected.emit()

    def clear_selection(self):
        self.device_table.clearSelection()
        self.active_server_row = None
        self.server_deselected.emit()
        self.device_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.device_table.setSelectionMode(QTableWidget.NoSelection)
        self.device_table.verticalHeader().setVisible(False)
        self.device_table.horizontalHeader().setStretchLastSection(True)
        self.device_table.setColumnWidth(0, 25)
        self.device_table.setColumnWidth(1, 120)
        self.device_table.horizontalHeader().setVisible(False)
        self.device_table.verticalHeader().setDefaultSectionSize(20)
        self.device_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.device_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.device_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        title_label = QLabel("Edge Servers")
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setContentsMargins(0, 0, 0, 0)
        title_label.setStyleSheet("margin-bottom:0px;padding-bottom:0px;margin-top:0px;padding-top:0px;")
        title_label.setSizePolicy(title_label.sizePolicy().horizontalPolicy(), QSizePolicy.Minimum)
        layout.addWidget(title_label)
        location_label = QLabel("Location")
        location_label.setAlignment(Qt.AlignCenter)
        location_label.setContentsMargins(0, 0, 0, 0)
        location_label.setStyleSheet("margin-bottom:0px;padding-bottom:0px;margin-top:0px;padding-top:0px;")
        location_label.setSizePolicy(location_label.sizePolicy().horizontalPolicy(), QSizePolicy.Minimum)
        layout.addWidget(location_label)
        layout.addWidget(self.location_selector)
        devices_label = QLabel("Devices")
        devices_label.setAlignment(Qt.AlignCenter)
        devices_label.setStyleSheet("margin-bottom:0px;padding-bottom:0px;margin-top:0px;padding-top:0px;")
        layout.addWidget(devices_label)
        layout.addWidget(self.device_table)
        self.setLayout(layout)

    def set_location_changed_callback(self, callback):
        self.location_selector.currentTextChanged.connect(callback)

    def update_table(self, servers):
        self.device_table.setRowCount(0)
        for i, server in enumerate(servers):
            desc = server.get("description", server.get("name", "Unnamed server"))
            status = server.get("status", "green")
            item_icon = QTableWidgetItem()
            item_icon.setIcon(self.status_icons.get(status, self.status_icons["green"]))
            item_icon.setText("")
            item_icon.setTextAlignment(Qt.AlignCenter)
            self.device_table.setItem(i, 0, item_icon)
            name_item = QTableWidgetItem(desc)
            self.device_table.setItem(i, 1, name_item)
    
    def update_health_status(self, server_name, health_status, tooltip_text):
        """Update the health status icon for a device.
        
        Args:
            server_name: The name of the server to update
            health_status: Status string ("OK", "WARNING", "CRITICAL", "FATAL")
            tooltip_text: Tooltip text to display on hover
        """
        # Map health status to icon colors
        status_icon_map = {
            "OK": "green",
            "WARNING": "yellow",
            "CRITICAL": "orange",  # Falls back to red if orange doesn't exist
            "FATAL": "red"
        }
        
        icon_status = status_icon_map.get(health_status, "green")
        
        # If orange icon doesn't exist and status is CRITICAL, use red
        if icon_status == "orange" and icon_status not in self.status_icons:
            icon_status = "red"
        
        # Find the row for this server
        location = self.location_selector.currentText()
        servers = self.servers_by_location.get(location, [])
        
        for i, server in enumerate(servers):
            if server.get("name") == server_name:
                # Update the status icon (column 0)
                status_item = self.device_table.item(i, 0)
                if status_item:
                    status_item.setIcon(self.status_icons.get(icon_status, self.status_icons["green"]))
                    status_item.setToolTip(tooltip_text)
                break