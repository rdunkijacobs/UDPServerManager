
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
    QFrame,
)
from PySide6.QtCore import Qt, QTimer
import config
# Import refactored panels
from .device_panel import DevicePanel
from .status_panel import StatusPanel
from .macro_dialog import MacroDialog
from core.workers.capstanDrive.message_creator_panel import MessageCreatorPanel

# Import UDPClientThread for UDP networking
from core.udp import UDPClientThread

# Import HealthMonitor for health checking
from core.health_monitor import HealthMonitor



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
        self.setMinimumWidth(config.WINDOW_MIN_WIDTH)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
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
        command_dict_path = os.path.join(os.path.dirname(__file__), '../../../../shared_dictionaries/command_dictionaries/capstanDrive_commandDictionary.json')
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

        # --- Status Panel (new) ---
        self.status_panel = StatusPanel()
        
        # --- Health Monitor (v2.01) ---
        self.health_monitor = None
        self.device_health_history = {}  # Track previous health status for each device
        if config.HEALTH_CHECK_ENABLED:
            self.health_monitor = HealthMonitor()
            # Connect health monitor signals
            self.health_monitor.health_status_updated.connect(self._on_health_status_updated)
            self.health_monitor.health_warning.connect(self._on_health_warning)
            self.health_monitor.health_critical.connect(self._on_health_critical)
            self.health_monitor.health_fatal.connect(self._on_health_fatal)
            self.health_monitor.escalate_to_controller.connect(self._on_escalate_to_controller)
            # Log message will be added after log_panel is created
            
            # Add manual check button to device panel area
            self.manual_check_button = QPushButton("Check Health")
            self.manual_check_button.setFixedHeight(25)
            self.manual_check_button.clicked.connect(self._on_manual_health_check)
            self.manual_check_button.setEnabled(False)  # Disabled until worker registered
            
            # Setup hourly ZULU broadcast timer
            self.zulu_broadcast_timer = QTimer(self)
            self.zulu_broadcast_timer.timeout.connect(self._on_hourly_zulu_broadcast)
            self.zulu_broadcast_timer.start(3600000)  # 1 hour = 3600000 ms

        # --- Log panel ---
        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        self.log_panel.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.log_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # --- Request box ---
        self.request_box = QTextEdit()
        self.request_box.setReadOnly(True)
        self.request_box.setFixedHeight(config.REQUEST_BOX_HEIGHT)
        self.request_box.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.request_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.request_box.setStyleSheet("background: #fffbe6; border: 1px solid #ccc; padding: 4px;")
        
        # --- Reply box ---
        self.reply_box = QTextEdit()
        self.reply_box.setReadOnly(True)
        self.reply_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.reply_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.reply_box.setStyleSheet("background: #e6f7ff; border: 1px solid #ccc; padding: 4px;")
        
        # --- Send button ---
        self.send_button = QPushButton("SEND")
        self.send_button.setFixedSize(config.SEND_BUTTON_WIDTH, config.SEND_BUTTON_HEIGHT)
        self.send_button.clicked.connect(self.on_send_button_clicked)

        # --- Abort button ---
        self.abort_button = QPushButton("ABORT")
        self.abort_button.setFixedSize(config.SEND_BUTTON_WIDTH, config.SEND_BUTTON_HEIGHT)
        self.abort_button.setEnabled(False)
        self.abort_button.setStyleSheet(
            "QPushButton:enabled { background-color: #c0392b; color: white; font-weight: bold; }"
        )
        self.abort_button.clicked.connect(self.on_abort_button_clicked)
        self._last_sent_message = None

        # --- Macro button ---
        self.macro_button = QPushButton("MACRO")
        self.macro_button.setFixedHeight(config.SEND_BUTTON_HEIGHT)
        self.macro_button.setToolTip("Open Macro Manager — record and step-run command sequences")
        self.macro_button.clicked.connect(self.on_macro_button_clicked)

        # --- IP-to-device-name lookup (built from servers.json) ---
        self._ip_name_map = {}
        for servers in self.servers_by_location.values():
            for s in servers:
                host = s.get("host") or s.get("ip")
                name = s.get("name")
                if host and name:
                    self._ip_name_map[host] = name

        # --- Macro dialog (kept as a reference so replies can be forwarded) ---
        self._current_device_name = ""
        self.macro_dialog = None

        # --- Delayed abort enable timer (1.5 s after send) ---
        self._abort_pending = False
        self._abort_enable_timer = QTimer(self)
        self._abort_enable_timer.setSingleShot(True)
        self._abort_enable_timer.setInterval(1500)
        self._abort_enable_timer.timeout.connect(self._on_abort_enable_timer)

        # --- Main layout: Two horizontal frames (Interactive top, Logging bottom) ---
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Interactive Frame (top) ---
        interactive_frame = QFrame()
        interactive_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        interactive_frame.setFixedHeight(config.INTERACTIVE_FRAME_HEIGHT)
        interactive_layout = QHBoxLayout()
        interactive_layout.setSpacing(5)
        interactive_layout.setContentsMargins(5, 5, 5, 5)
        
        # Left: Device Panel Frame
        device_frame = QFrame()
        device_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        device_frame.setFixedWidth(config.DEVICE_PANEL_WIDTH)
        device_layout = QVBoxLayout()
        device_layout.setContentsMargins(0, 0, 0, 0)
        device_layout.addWidget(self.device_panel)
        # Add manual health check button if health monitoring enabled
        if config.HEALTH_CHECK_ENABLED:
            device_layout.addWidget(self.manual_check_button)
        device_frame.setLayout(device_layout)
        interactive_layout.addWidget(device_frame)
        
        # Middle: Message Creator Panel Frame
        message_frame = QFrame()
        message_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        message_layout = QVBoxLayout()
        message_layout.setContentsMargins(5, 5, 5, 5)
        message_layout.addWidget(self.message_creator_panel)
        message_frame.setLayout(message_layout)
        interactive_layout.addWidget(message_frame)
        
        # Right: Request/Reply/Send Frame
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        right_frame.setFixedWidth(200)  # Fixed width for right panel
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        send_abort_layout = QHBoxLayout()
        send_abort_layout.setSpacing(5)
        send_abort_layout.addWidget(self.send_button)
        send_abort_layout.addWidget(self.abort_button)
        right_layout.addLayout(send_abort_layout)
        right_layout.addWidget(self.macro_button)
        right_layout.addWidget(QLabel("Request:"))
        right_layout.addWidget(self.request_box)
        right_layout.addWidget(QLabel("Reply:"))
        right_layout.addWidget(self.reply_box)
        
        right_frame.setLayout(right_layout)
        interactive_layout.addWidget(right_frame)
        
        interactive_frame.setLayout(interactive_layout)
        main_layout.addWidget(interactive_frame)
        
        # --- Status Frame (middle) ---
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        status_frame.setFixedHeight(config.STATUS_FRAME_HEIGHT)
        status_layout = QVBoxLayout()
        status_layout.setSpacing(2)
        status_layout.setContentsMargins(5, 5, 5, 5)
        status_layout.addWidget(QLabel("Status"))
        status_layout.addWidget(self.status_panel)
        status_frame.setLayout(status_layout)
        main_layout.addWidget(status_frame)
        
        # --- Logging Frame (bottom) ---
        logging_frame = QFrame()
        logging_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        logging_frame.setFixedHeight(config.LOGGING_FRAME_HEIGHT)
        logging_layout = QVBoxLayout()
        logging_layout.setSpacing(2)
        logging_layout.setContentsMargins(5, 5, 5, 5)
        logging_layout.addWidget(QLabel("Log"))
        logging_layout.addWidget(self.log_panel)
        logging_frame.setLayout(logging_layout)
        main_layout.addWidget(logging_frame)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect DevicePanel signals
        self.device_panel.server_selected.connect(self.handle_device_selected)
        self.device_panel.server_deselected.connect(self.handle_device_deselected)
        
        # Connect MessageCreatorPanel signal to clear reply box
        self.message_creator_panel.user_input_changed.connect(self.clear_reply_box)

        # Optionally, connect message preview to log panel or other UI as needed
        
        # Log health monitor initialization status (after log_panel is created)
        if config.HEALTH_CHECK_ENABLED and self.health_monitor:
            self.log_message("[HealthMonitor] Health monitoring system initialized")

        print("[DEBUG] MainWindow initialized with MessageCreatorPanel")
    
    def on_send_button_clicked(self):
        """Handle send button click - get message from panel and send it."""
        msg = self.message_creator_panel.assembled_output.text()
        if msg and '□' not in msg:
            self._last_sent_message = msg
            self.send_udp_message(msg)
            self.request_box.setText(f"Sent: {msg}")
            self.reply_box.clear()
            self._abort_pending = True
            self._abort_enable_timer.start()
        elif '□' in msg:
            self.request_box.setText("Fill in all required fields first.")
        else:
            self.request_box.setText("No message to send")
    
    def log_message(self, msg):
        """Append message to log panel and auto-scroll to bottom."""
        self.log_panel.append(msg)
        self.log_panel.ensureCursorVisible()
    
    def log_reply(self, msg):
        """Append only actual UDP received messages to reply box, with IP→name translation."""
        if msg.startswith("Received from"):
            self.reply_box.append(self._translate_received_message(msg))
            self.reply_box.ensureCursorVisible()
            # Reply arrived — cancel pending abort
            self._abort_pending = False
            self._abort_enable_timer.stop()
            self.abort_button.setEnabled(False)
            # Forward to macro dialog if it is open and awaiting a step reply
            if self.macro_dialog is not None and self.macro_dialog.isVisible():
                self.macro_dialog.receive_reply(msg)

    def clear_reply_box(self):
        """Clear the reply box when user changes any input."""
        self.reply_box.clear()
        self._abort_pending = False
        self._abort_enable_timer.stop()
        self.abort_button.setEnabled(False)

    def on_macro_button_clicked(self):
        """Open (or raise) the Macro Manager dialog."""
        if self.macro_dialog is None or not self.macro_dialog.isVisible():
            self.macro_dialog = MacroDialog(
                get_current_message=lambda: self.message_creator_panel.assembled_output.text(),
                send_fn=self.send_udp_message,
                device_name=self._current_device_name,
                parent=self,
            )
        self.macro_dialog.show()
        self.macro_dialog.raise_()
        self.macro_dialog.activateWindow()

    def on_abort_button_clicked(self):
        """Abandon the last sent message — no reply expected."""
        self._abort_pending = False
        self._abort_enable_timer.stop()
        self.log_message(f"[ABORTED] No reply received for: {self._last_sent_message}")
        self.request_box.setText(f"[ABORTED] {self._last_sent_message}")
        self.reply_box.clear()
        self.abort_button.setEnabled(False)
        self._last_sent_message = None

    def _on_abort_enable_timer(self):
        """Called 1.5 s after send — enable ABORT only if still waiting for a reply."""
        if self._abort_pending:
            self.abort_button.setEnabled(True)

    def _translate_received_message(self, msg):
        """Replace raw IP address in a 'Received from' message with the device name.

        Input:  "Received from ('192.168.1.244', 2222): OK"
        Output: "Received from capstanDrive (192.168.1.244:2222): OK"
        """
        import re
        match = re.match(r"Received from \('([\d.]+)', (\d+)\): (.*)", msg, re.DOTALL)
        if match:
            ip, port, payload = match.groups()
            name = self._ip_name_map.get(ip, ip)  # Fall back to raw IP if not found
            return f"From {name}: {payload}"
        return msg  # Return unchanged if format not recognised
    
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
            self.log_panel.ensureCursorVisible()
        else:
            self.log_panel.append("[UI] No UDP connection to send message.")
            self.log_panel.ensureCursorVisible()

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
        server_name = server.get('name', 'Unnamed')
        if host and port:
            self._current_device_name = server_name
            self.log_panel.append(f"Connecting to {host}:{port}...")
            self.log_panel.ensureCursorVisible()
            self.udp_thread = UDPClientThread(host, port, server_name)
            self.udp_thread.message_received.connect(self.log_message)
            self.udp_thread.message_received.connect(self.log_reply)
            self.udp_thread.start()
            # Update message creator for this server
            self.message_creator_panel.set_server(server)
            
            # --- Health Monitor Integration (v2.01) ---
            if config.HEALTH_CHECK_ENABLED and self.health_monitor:
                # Get requested metrics from server config (if available)
                requested_metrics = server.get("health_metrics", ["uptime", "temperature", "cpu", "memory"])
                
                # Register worker with health monitor
                self.health_monitor.register_worker(
                    server_name,
                    self.udp_thread,
                    requested_metrics
                )
                
                # Start health monitoring only if not already running
                if not self.health_monitor.timer.isActive():
                    self.health_monitor.start()
                
                # Enable manual check button
                if hasattr(self, 'manual_check_button'):
                    self.manual_check_button.setEnabled(True)
                
                self.log_panel.append(f"[HealthMonitor] Registered worker: {server_name}")
                self.log_panel.ensureCursorVisible()
        else:
            self.log_panel.append("No host/port info for selected server.")
            self.log_panel.ensureCursorVisible()   

    def handle_device_deselected(self):
        # Unregister from health monitor first
        if config.HEALTH_CHECK_ENABLED and self.health_monitor and hasattr(self, "udp_thread"):
            if self.udp_thread is not None:
                # Get the server name from the last selected device
                # (We need to track this or unregister all)
                self.health_monitor.unregister_all_workers()
                self.health_monitor.stop()  # Stop health checking
                self.log_panel.append("[HealthMonitor] Stopped and unregistered all workers")
                
                # Disable manual check button
                if hasattr(self, 'manual_check_button'):
                    self.manual_check_button.setEnabled(False)
        
        self._current_device_name = ""
        # Stop UDP thread if nothing selected
        if hasattr(self, "udp_thread") and self.udp_thread is not None:
            self.udp_thread.stop()
            self.udp_thread = None
        # Clear message creator fields
        self.message_creator_panel.clear_fields()
        
    # --- Status Panel Helper Methods ---
    def update_status_table(self, data_dict):
        """
        Update the status panel table with device status information.
        
        Args:
            data_dict: Dictionary of item_name: item_data pairs
            
        Example:
            self.update_status_table({
                'Device': 'CapstanDrive',
                'Status': 'Connected',
                'Uptime': '12:34:56',
                'Temperature': '45°C',
                'LED Status': 'Green ON'
            })
        """
        self.status_panel.update_table(data_dict)
    
    def update_status_text(self, text):
        """
        Update the text box in split mode.
        
        Args:
            text: Status text to display
        """
        self.status_panel.set_text(text)
    
    def update_status_image(self, image_path):
        """
        Update the image display in split mode.
        
        Args:
            image_path: Path to image file or QPixmap object
        """
        self.status_panel.set_image(image_path)
    
    def update_status_video(self, video_path):
        """
        Load and display a video in the status panel.
        
        Args:
            video_path: Path to video file (mp4, avi, mov, etc.) or streaming URL
            
        Examples:
            # Local video file
            self.update_status_video('C:/videos/device_animation.mp4')
            
            # Network stream (basic support, full implementation in Pi 4B phase)
            self.update_status_video('http://192.168.1.100:8080/stream.m3u8')
        """
        # Auto-detect if it's a URL or file path
        is_stream = video_path.startswith(('http://', 'https://', 'rtsp://', 'rtp://'))
        self.status_panel.set_video(video_path, is_stream=is_stream)
    
    def control_video(self, action):
        """
        Control video playback.
        
        Args:
            action: 'play', 'pause', or 'stop'
        """
        if action == 'play':
            self.status_panel.play_video()
        elif action == 'pause':
            self.status_panel.pause_video()
        elif action == 'stop':
            self.status_panel.stop_video()
    
    # ========================================================================
    # FUTURE FEATURE: Live Video Streaming (Raspberry Pi 4B Phase)
    # ========================================================================
    
    def connect_live_stream(self, stream_url, protocol='http'):
        """
        PLACEHOLDER: Connect to a live video stream from network source.
        
        This will be fully implemented when the generic worker application
        is extended to support Raspberry Pi 4B with camera/video capabilities.
        
        Planned features:
        - Real-time video from Pi Camera modules
        - IP camera streams (RTSP, HTTP)
        - WebRTC for low-latency streaming
        - Multi-device video monitoring
        
        Args:
            stream_url: URL of the live stream source
            protocol: Protocol type ('http', 'rtsp', 'webrtc')
            
        Example:
            # Connect to Raspberry Pi 4B video stream
            self.connect_live_stream('http://192.168.1.50:8080/stream.m3u8')
        """
        self.status_panel.set_live_stream(stream_url, protocol)
        self.log_message(f"[FUTURE] Connecting to live stream: {stream_url} ({protocol})")
    
    def get_stream_quality(self):
        """
        PLACEHOLDER: Get current stream quality metrics.
        
        Returns stream status from the status panel (to be fully implemented).
        """
        return self.status_panel.get_stream_status()
        # ========================================================================
    # HEALTH MONITOR HANDLERS (v2.01)
    # ========================================================================
    
    def _on_health_status_updated(self, server_name, health_status):
        """Handle health status updates from HealthMonitor."""
        status_text = health_status.get("status", "UNKNOWN")
        tooltip_text = health_status.get("tooltip", "")
        
        # Check for ZULU sync triggers
        previous_status = self.device_health_history.get(server_name)
        
        # First contact: send ZULU sync
        if previous_status is None:
            self.log_message(f"[ZULU] First contact with {server_name} - sending time sync")
            self.send_zulu_sync(server_name=server_name)
        
        # Re-established contact after FATAL: send ZULU sync
        elif previous_status == "FATAL" and status_text in ["OK", "WARNING", "CRITICAL"]:
            self.log_message(f"[ZULU] {server_name} re-established contact - sending time sync")
            self.send_zulu_sync(server_name=server_name)
        
        # Update history
        self.device_health_history[server_name] = status_text
        
        # Update device panel icon color
        self.device_panel.update_health_status(server_name, status_text, tooltip_text)
        
        # Log status change if not OK
        if status_text != "OK":
            import time as time_module
            last_check_timestamp = health_status.get("last_check", 0)
            last_check = time_module.strftime('%H:%M:%S', time_module.localtime(last_check_timestamp)) if last_check_timestamp > 0 else "N/A"
            
            # Add transit anomaly info if detected
            if health_status.get("transit_anomaly", False):
                window_size = health_status.get("transit_window_size", 0)
                self.log_message(f"[HealthMonitor] {server_name}: {status_text} - Transit anomaly ({window_size}/18 samples) (Last check: {last_check})")
            else:
                self.log_message(f"[HealthMonitor] {server_name}: {status_text} (Last check: {last_check})")
    
    def _on_health_warning(self, server_name, message):
        """Handle health WARNING level."""
        self.log_message(f"[HealthMonitor WARNING] {server_name}: {message}")
    
    def _on_health_critical(self, server_name, message):
        """Handle health CRITICAL level - show message box."""
        from PySide6.QtWidgets import QMessageBox
        self.log_message(f"[HealthMonitor CRITICAL] {server_name}: {message}")
        
        # Show warning dialog
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Health Check Critical")
        msg_box.setText(f"Device {server_name} health check CRITICAL")
        msg_box.setInformativeText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def _on_health_fatal(self, server_name, message):
        """Handle health FATAL level - show critical message box."""
        from PySide6.QtWidgets import QMessageBox
        self.log_message(f"[HealthMonitor FATAL] {server_name}: {message}")
        
        # Show critical error dialog
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Health Check Fatal")
        msg_box.setText(f"Device {server_name} health check FATAL")
        msg_box.setInformativeText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def _on_escalate_to_controller(self, server_name, status_dict):
        """Handle escalation to controller level."""
        error_level = status_dict.get('status', 'UNKNOWN')
        message = status_dict.get('last_error', 'No details available')
        self.log_message(f"[HealthMonitor ESCALATE] {server_name} [{error_level}]: {message}")
        # Future: Send notification to central controller system
    
    def _on_manual_health_check(self):
        """Handle manual health check button click."""
        if self.health_monitor:
            self.health_monitor.trigger_manual_check()
            self.log_message("[HealthMonitor] Manual health check triggered")
    
    def _on_hourly_zulu_broadcast(self):
        """Send ZULU time sync broadcast every hour."""
        self.log_message("[ZULU] Hourly broadcast - syncing all devices")
        self.send_zulu_sync(broadcast=True)
    
    def send_zulu_sync(self, server_name=None, broadcast=False):
        """Send ZULU time synchronization to device(s).
        
        Args:
            server_name: Specific server to sync (unicast)
            broadcast: If True, send to all devices (overrides server_name)
        """
        if not self.health_monitor:
            return
        
        if broadcast:
            # Send to all registered workers
            for worker in self.health_monitor.workers.values():
                if hasattr(worker, 'send_zulu_sync'):
                    worker.send_zulu_sync(broadcast=True)
                    break  # Only need to send once for broadcast
        elif server_name:
            # Send to specific worker
            worker = self.health_monitor.workers.get(server_name)
            if worker and hasattr(worker, 'send_zulu_sync'):
                worker.send_zulu_sync(broadcast=False)
