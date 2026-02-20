from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QTextEdit, QLabel, QPushButton,
    QStackedWidget, QHeaderView, QSlider
)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class StatusPanel(QWidget):
    """
    Status panel that can display either:
    1. A table with item name | item data columns
    2. A split view with text box on left and image/video display on right
    
    Video Support:
    - Local files: MP4, AVI, MOV and other common video formats
    - Network streams: HTTP, HTTPS, RTSP (basic support)
    - Built-in playback controls (Play, Pause, Stop)
    - Seekable timeline slider
    - Time display (current / total duration)
    
    FUTURE (Raspberry Pi 4B Phase):
    - Live streaming from Pi Camera modules
    - Enhanced network stream support (WebRTC, RTP)
    - Stream health monitoring and auto-reconnection
    - Multi-camera view support
    - Network quality indicators
    
    Usage Examples:
        # Display an image
        status_panel.set_image('path/to/image.png')
        
        # Display a local video with controls
        status_panel.set_video('path/to/video.mp4')
        status_panel.play_video()  # Start playback
        
        # Display network stream (basic support)
        status_panel.set_video('http://192.168.1.100/stream.m3u8', is_stream=True)
        
        # Update status table
        status_panel.update_table({
            'Device': 'CapstanDrive',
            'Status': 'Running',
            'Temperature': '45°C'
        })
        
        # Future: Live stream from Raspberry Pi 4B
        status_panel.set_live_stream('http://pi4b.local:8080/stream')
    """
    
    def __init__(self):
        super().__init__()
        
        # Create stacked widget to switch between modes
        self.stacked_widget = QStackedWidget()
        
        # Create table view (mode 0)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Item Name", "Item Data"])
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Create split view (mode 1)
        self.split_widget = QWidget()
        split_layout = QHBoxLayout()
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(5)
        
        # Text box on left
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setPlaceholderText("Status text appears here...")
        
        # Right side: Stacked widget for image or video
        self.media_stack = QStackedWidget()
        
        # Image display widget
        self.image_widget = QWidget()
        image_layout = QVBoxLayout()
        image_layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        self.image_label.setScaledContents(False)
        self.image_label.setText("No Image")
        image_layout.addWidget(self.image_label)
        self.image_widget.setLayout(image_layout)
        
        # Video display widget with controls
        self.video_widget_container = QWidget()
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(5)
        
        # Video player and widget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("border: 1px solid #ccc; background: #000;")
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Video controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)
        
        self.play_button = QPushButton("▶ Play")
        self.pause_button = QPushButton("⏸ Pause")
        self.stop_button = QPushButton("⏹ Stop")
        
        self.play_button.setFixedWidth(70)
        self.pause_button.setFixedWidth(70)
        self.stop_button.setFixedWidth(70)
        
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        
        # Position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        
        # Time labels
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFixedWidth(100)
        
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.position_slider)
        controls_layout.addWidget(self.time_label)
        
        video_layout.addWidget(self.video_widget)
        video_layout.addLayout(controls_layout)
        self.video_widget_container.setLayout(video_layout)
        
        # Add both to media stack
        self.media_stack.addWidget(self.image_widget)  # Index 0
        self.media_stack.addWidget(self.video_widget_container)  # Index 1
        self.media_stack.setCurrentIndex(0)  # Default to image
        
        # Connect media player signals
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        
        split_layout.addWidget(self.text_box, 1)  # Text takes 1 part
        split_layout.addWidget(self.media_stack, 1)  # Media takes 1 part
        
        self.split_widget.setLayout(split_layout)
        
        # Add both modes to stacked widget
        self.stacked_widget.addWidget(self.table_widget)  # Index 0
        self.stacked_widget.addWidget(self.split_widget)  # Index 1
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Mode selector buttons
        button_layout = QHBoxLayout()
        self.table_mode_button = QPushButton("Table View")
        self.split_mode_button = QPushButton("Text + Image View")
        
        self.table_mode_button.clicked.connect(lambda: self.set_mode(0))
        self.split_mode_button.clicked.connect(lambda: self.set_mode(1))
        
        button_layout.addWidget(self.table_mode_button)
        button_layout.addWidget(self.split_mode_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)
        
        self.setLayout(main_layout)
        
        # Set default mode
        self.set_mode(0)
    
    def set_mode(self, mode):
        """Switch between table (0) and split (1) modes."""
        self.stacked_widget.setCurrentIndex(mode)
        
        # Update button styles to show active mode
        if mode == 0:
            self.table_mode_button.setStyleSheet("font-weight: bold;")
            self.split_mode_button.setStyleSheet("")
        else:
            self.table_mode_button.setStyleSheet("")
            self.split_mode_button.setStyleSheet("font-weight: bold;")
    
    def add_table_row(self, item_name, item_data):
        """Add a row to the table."""
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(str(item_name)))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(item_data)))
    
    def clear_table(self):
        """Clear all rows from the table."""
        self.table_widget.setRowCount(0)
    
    def update_table(self, data_dict):
        """Update table with a dictionary of item_name: item_data pairs."""
        self.clear_table()
        for name, data in data_dict.items():
            self.add_table_row(name, data)
    
    def set_text(self, text):
        """Set the text in the text box (split mode)."""
        self.text_box.setPlainText(text)
    
    def append_text(self, text):
        """Append text to the text box (split mode)."""
        self.text_box.append(text)
    
    def clear_text(self):
        """Clear the text box."""
        self.text_box.clear()
    
    def set_image(self, image_path_or_pixmap):
        """
        Set the image to display. Maintains aspect ratio and sets height to frame height.
        
        Args:
            image_path_or_pixmap: Either a file path (str) or QPixmap object
        """
        if isinstance(image_path_or_pixmap, str):
            pixmap = QPixmap(image_path_or_pixmap)
        else:
            pixmap = image_path_or_pixmap
        
        if pixmap.isNull():
            self.image_label.setText("Image load failed")
            return
        
        # Scale to fit the label height while maintaining aspect ratio
        scaled_pixmap = pixmap.scaledToHeight(
            self.image_label.height(), 
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
    
    def clear_image(self):
        """Clear the image display."""
        self.image_label.clear()
        self.image_label.setText("No Image")
        self.media_stack.setCurrentIndex(0)  # Switch to image view
    
    def set_video(self, video_source, is_stream=False):
        """
        Set a video to play in the media area.
        
        Supports both local files and streaming URLs.
        
        Args:
            video_source: Path to video file (mp4, avi, etc.) or URL for streaming
            is_stream: If True, treats video_source as a URL (http://, rtsp://, etc.)
                      If False, treats as local file path
        
        Examples:
            # Local file
            set_video('C:/videos/demo.mp4')
            
            # HTTP stream (future: Raspberry Pi 4B phase)
            set_video('http://192.168.1.100:8080/stream', is_stream=True)
            
            # RTSP stream (future: Raspberry Pi 4B phase)
            set_video('rtsp://192.168.1.100:8554/stream', is_stream=True)
        """
        if isinstance(video_source, QUrl):
            url = video_source
        elif is_stream:
            # For streaming URLs (HTTP, RTSP, etc.)
            url = QUrl(video_source)
        else:
            # For local file paths
            url = QUrl.fromLocalFile(video_source)
        
        self.media_player.setSource(url)
        self.media_stack.setCurrentIndex(1)  # Switch to video view
        # Optionally auto-play
        # self.media_player.play()
    
    def play_video(self):
        """Start or resume video playback."""
        self.media_player.play()
    
    def pause_video(self):
        """Pause video playback."""
        self.media_player.pause()
    
    def stop_video(self):
        """Stop video playback and reset to beginning."""
        self.media_player.stop()
    
    def set_position(self, position):
        """Set video playback position."""
        self.media_player.setPosition(position)
    
    def position_changed(self, position):
        """Update position slider and time label."""
        self.position_slider.setValue(position)
        self.update_time_label(position, self.media_player.duration())
    
    def duration_changed(self, duration):
        """Update slider range when video duration is known."""
        self.position_slider.setRange(0, duration)
        self.update_time_label(self.media_player.position(), duration)
    
    def update_time_label(self, position, duration):
        """Update the time display label."""
        def format_time(ms):
            s = ms // 1000
            m = s // 60
            s = s % 60
            return f"{m:02d}:{s:02d}"
        
        current = format_time(position)
        total = format_time(duration) if duration > 0 else "00:00"
        self.time_label.setText(f"{current} / {total}")
    
    def clear_video(self):
        """Stop and clear the video."""
        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self.media_stack.setCurrentIndex(0)  # Switch back to image view
    
    # ========================================================================
    # FUTURE FEATURE: Live Video Streaming (Raspberry Pi 4B Phase)
    # ========================================================================
    
    def set_live_stream(self, stream_url, protocol='http'):
        """
        PLACEHOLDER: Connect to a live video stream from a network source.
        
        This method will be fully implemented in the Raspberry Pi 4B phase
        when the generic worker application supports live video streaming.
        
        Planned support for:
        - HTTP/HTTPS streams (HLS, DASH)
        - RTSP streams from IP cameras
        - WebRTC streams
        - Custom UDP/RTP streams
        
        Args:
            stream_url: URL of the live stream
                       Examples:
                       - 'http://192.168.1.100:8080/stream.m3u8' (HLS)
                       - 'rtsp://192.168.1.100:554/live' (RTSP)
            protocol: Stream protocol ('http', 'rtsp', 'webrtc', 'rtp')
        
        Future enhancements:
        - Stream health monitoring
        - Automatic reconnection on connection loss
        - Buffering indicators
        - Network statistics (latency, bandwidth, dropped frames)
        - Multi-camera support
        """
        # Current implementation: Basic URL streaming support
        # Full implementation will include error handling, reconnection logic, etc.
        self.set_video(stream_url, is_stream=True)
        
        # TODO (Raspberry Pi 4B Phase):
        # - Add stream health monitoring
        # - Implement reconnection logic
        # - Add buffering indicators
        # - Network quality indicators
        # - Multiple stream source failover
        pass
    
    def get_stream_status(self):
        """
        PLACEHOLDER: Get status of current live stream.
        
        Returns:
            dict: Stream status information (to be implemented)
                  {
                      'connected': bool,
                      'latency_ms': int,
                      'bandwidth_mbps': float,
                      'dropped_frames': int,
                      'buffer_health': str ('good', 'warning', 'critical')
                  }
        """
        # TODO (Raspberry Pi 4B Phase): Implement stream monitoring
        return {
            'connected': False,
            'latency_ms': 0,
            'bandwidth_mbps': 0.0,
            'dropped_frames': 0,
            'buffer_health': 'unknown'
        }
