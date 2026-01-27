
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QTextEdit,
    QLabel,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt
# Import refactored panels
from .device_panel import DevicePanel
from core.workers.capstanDrive.message_creator_panel import MessageCreatorPanel

# Import UDPClientThread for UDP networking
from core.udp import UDPClientThread




from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QTextEdit,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    # ...existing code...
    def __init__(self, servers_by_location, status_icons):
        super().__init__()
        self.setWindowTitle("UDP Supervisor (MIS)")
        self.setMinimumWidth(1024)
        self.resize(1600, 900)  # Set initial window size to 1600px wide
        self.servers_by_location = servers_by_location
        self.status_icons = status_icons

        # --- Device panel ---
        self.device_panel = DevicePanel(
            self.servers_by_location, self.status_icons
        )

        # --- Load command dictionary and config ---
        import importlib.util, os, json
        self._command_dict = None
        self._command_config = None
        command_dict_path = os.path.join(os.path.dirname(__file__), '../../core/workers/capstanDrive/capstanDrive_commandDictionary.json')
        try:
            with open(command_dict_path, 'r') as f:
                self._command_dict = json.load(f)
        except Exception as e:
            print(f"Error loading command dictionary: {e}")
        config_path = os.path.join(os.path.dirname(__file__), '../../core/workers/capstanDrive/capstanDrive_config.py')
        try:
            spec = importlib.util.spec_from_file_location('capstanDrive_config', config_path)
            config_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_mod)
            self._command_config = config_mod
        except Exception as e:
            print(f"Error loading config: {e}")

        # --- Message Creator Panel (modular) ---
        self.message_creator_panel = MessageCreatorPanel(self._command_dict, self._command_config)

        # --- Log panel ---
        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)

        # --- Main layout ---
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.device_panel, alignment=Qt.AlignTop | Qt.AlignLeft)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.message_creator_panel, alignment=Qt.AlignTop | Qt.AlignRight)
        right_layout.addWidget(QLabel("Log"))
        right_layout.addWidget(self.log_panel)
        main_layout.addLayout(right_layout)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect DevicePanel signals
        self.device_panel.server_selected.connect(self.handle_device_selected)
        self.device_panel.server_deselected.connect(self.handle_device_deselected)

        # Connect MessageCreatorPanel send signal to UDP logic
        self.message_creator_panel.send_message_signal.connect(self.send_udp_message)

        # Optionally, connect message preview to log panel or other UI as needed

        print("[DEBUG] MainWindow initialized with MessageCreatorPanel")
    # Message assembly now handled by MessageCreatorPanel

    # Param dropdown logic now handled by MessageCreatorPanel
    # Mode dropdown logic now handled by MessageCreatorPanel

    # Command dropdown logic now handled by MessageCreatorPanel

    # Device selection log now handled by DevicePanel signals

    # Device table update now handled by DevicePanel

    # Param fields now handled by MessageCreatorPanel

    def send_udp_message(self, msg):
        # Send via UDP thread if available
        if hasattr(self, "udp_thread") and self.udp_thread is not None:
            self.udp_thread.send_message(msg)
            self.log_panel.append(f"[UI] Sent: {msg}")
        else:
            self.log_panel.append("[UI] No UDP connection to send message.")

        # ...existing code...

    # No QSettings/restore in minimal implementation
    # Device list update now handled by DevicePanel

    # Device selection/connection now handled by DevicePanel signals

    def handle_device_selected(self, server):
        # Log the selection
        self.log_panel.append(
            f"[UI] Selected server: {server.get('name', 'Unnamed')} ({server.get('host', '')}:{server.get('port', '')})"
        )
        self.log_panel.ensureCursorVisible()
        # --- UDP Networking Integration ---
        if hasattr(self, "udp_thread") and self.udp_thread is not None:
            self.udp_thread.stop()
            self.udp_thread = None
        host = server.get("host") or server.get("ip")
        port = server.get("port")
        if host and port:
            self.log_panel.append(f"Connecting to {host}:{port}...")
            self.log_panel.ensureCursorVisible()
            self.udp_thread = UDPClientThread(host, port)
            self.udp_thread.message_received.connect(self.log_panel.append)
            self.udp_thread.start()
            # Update message creator for this server
            self.message_creator_panel.set_server(server)
        else:
            self.log_panel.append("No host/port info for selected server.")
            self.log_panel.ensureCursorVisible()

    def handle_device_deselected(self):
        # Stop UDP thread if nothing selected
        if hasattr(self, "udp_thread") and self.udp_thread is not None:
            self.udp_thread.stop()
            self.udp_thread = None
        # Clear message creator fields
        self.message_creator_panel.clear_fields()
