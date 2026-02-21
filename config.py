# UI Configuration Settings
# All dimensions are in pixels unless otherwise specified

# Main Window Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 800

# Frame Heights
LOGGING_FRAME_HEIGHT = 200
STATUS_FRAME_HEIGHT = 350  # New status panel between interactive and logging
INTERACTIVE_FRAME_HEIGHT = 350  # Reduced by 50% from original 700px

# Device Panel Settings (Left Frame)
DEVICE_PANEL_WIDTH = 200

# Message Creator Panel Settings (Middle Frame)
DROPDOWN_WIDTH = 250
LABEL_WIDTH = 85  # Wide enough for "Parameter X:" labels

# Assembly Message Output
MESSAGE_OUTPUT_MIN_WIDTH = 300
MESSAGE_OUTPUT_HEIGHT = 25

# Right Frame Settings (Request/Reply/Send)
REQUEST_BOX_HEIGHT = 50  # 2 lines high
SEND_BUTTON_WIDTH = 80
SEND_BUTTON_HEIGHT = 40
# Reply box height calculated dynamically: INTERACTIVE_FRAME_HEIGHT - REQUEST_BOX_HEIGHT - SEND_BUTTON_HEIGHT - margins

# Spacing Settings
VERTICAL_SPACING = 2  # Spacing between rows
HORIZONTAL_SPACING = 4  # Spacing within rows

# ============================================================================
# APPLICATION VERSION
# ============================================================================
VERSION = "2.01"

# ============================================================================
# HEALTH MONITORING (FrameStatus) - v2.01
# ============================================================================

# Master enable/disable for entire health monitoring system
# Set to False during initial development/debugging
HEALTH_CHECK_ENABLED = False  # Disabled

# Target interval for complete round-robin cycle (seconds)
# Each registered worker checked once per cycle
HEALTH_CHECK_ROUND_ROBIN_INTERVAL = 10.0

# Timeout waiting for PONG response from individual device (seconds)
# No response within this time = failure
HEALTH_CHECK_PONG_TIMEOUT = 1.0

# Sliding window configuration for failure tracking
HEALTH_CHECK_WINDOW_SIZE = 10           # M: Total checks tracked in sliding window
HEALTH_CHECK_FATAL_THRESHOLD = 3        # N: Failures out of M checks = FATAL

# Slow response tracking for WARNING level
HEALTH_CHECK_SLOW_WINDOW = 5            # Track last 5 responses for slow detection
HEALTH_CHECK_SLOW_THRESHOLD = 2         # 2 out of 5 slow responses = WARNING
HEALTH_CHECK_SLOW_RESPONSE_MS = 1000    # Response time > 1000ms = "slow"

# Transit time statistical analysis (3-minute window)
HEALTH_CHECK_TRANSIT_WINDOW = 18        # 3 minutes at 10s cycle = 18 checks
HEALTH_CHECK_TRANSIT_STDDEV_THRESHOLD = 2.0  # Warning if > 2 std deviations from mean

# Health check priority (lowest priority - never blocks normal operations)
HEALTH_CHECK_PRIORITY = -1

# Logging level for health monitoring
# Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
# Only warnings and above logged by default
HEALTH_CHECK_LOG_LEVEL = 'WARNING'

# Health status indicator colors for device panel
HEALTH_STATUS_COLORS = {
    'healthy': '#2ECC71',      # Green
    'warning': '#F39C12',      # Orange  
    'critical': '#E74C3C',     # Red
    'fatal': '#8B0000',        # Dark Red
    'unknown': '#95A5A6'       # Gray
}

# Standard health metrics (recommended for all devices)
# Devices may support additional custom metrics
STANDARD_HEALTH_METRICS = ['uptime', 'mem', 'errors']
