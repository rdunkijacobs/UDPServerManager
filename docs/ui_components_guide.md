# UI Components Guide

**Document Version:** 1.0  
**Last Updated:** February 19, 2026  
**Application Version:** UDP Server Manager v2.0+

---

## Table of Contents

1. [Overview](#overview)
2. [Main Window Layout](#main-window-layout)
3. [Device Panel](#device-panel)
4. [Message Creator Panel](#message-creator-panel)
5. [Status Panel](#status-panel)
6. [Send/Reply Panel](#sendreply-panel)
7. [Logging Panel](#logging-panel)
8. [UI Customization](#ui-customization)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The UDP Server Manager features a modern, Qt-based graphical user interface designed for efficient device management and monitoring. The interface is organized into three main horizontal tiers, each serving distinct purposes in the workflow.

### Design Philosophy

- **Task-Oriented Layout:** Components arranged by workflow stage
- **Real-Time Updates:** Live status monitoring and feedback
- **Minimal Clicks:** Hierarchical menus reduce navigation
- **Contextual Display:** Parameters shown only when relevant
- **Visual Feedback:** Color-coded status indicators
- **Professional Appearance:** Clean, organized interface suitable for industrial applications

### Window Specifications

- **Default Size:** 800 x 900 pixels
- **Minimum Width:** 800 pixels
- **Layout:** Three-tier vertical split with fixed frame heights
- **Resizable:** Horizontal expansion supported

---

## Main Window Layout

The application window is divided into three horizontal frames:

### Frame Structure

| Frame | Height | Purpose | Contents |
|-------|--------|---------|----------|
| Interactive Frame | 350px | Command creation and device selection | Device Panel, Message Creator, Send/Reply Panel |
| Status Frame | 350px | Device status and multimedia display | Status Panel with table/split modes |
| Logging Frame | 200px | Application and communication logs | Scrollable log text area |

### Visual Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│  Interactive Frame (350px)                              │
│  ┌─────────┬───────────────────────┬──────────────┐   │
│  │ Device  │  Message Creator      │ Send/Reply   │   │
│  │ Panel   │  Panel                │ Panel        │   │
│  │         │                       │              │   │
│  └─────────┴───────────────────────┴──────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Status Frame (350px)                                   │
│  ┌───────────────────────────────────────────────────┐ │
│  │  [Table View] [Text + Image View]                 │ │
│  │                                                    │ │
│  │  Status content (table or split display)          │ │
│  │                                                    │ │
│  └───────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Logging Frame (200px)                                  │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Log:                                              │ │
│  │  [Timestamped application and network logs]        │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Device Panel

**Location:** Left column of Interactive Frame  
**Width:** 200px (fixed)  
**File:** `app/ui/device_panel.py`

### Purpose

The Device Panel provides device selection and connection management with visual status indicators.

### Components

#### 1. Location Dropdown

**Purpose:** Filter devices by physical location

**Features:**
- Populated from server configuration file
- Groups devices by geographical or logical location
- Dynamically updates based on server list
- First location selected by default

**Usage:**
```
Click dropdown → Select location → Device list updates
```

#### 2. Server List

**Purpose:** Display and select individual devices

**Features:**
- One row per configured device
- Status icon indicates connection state
- Color-coded status indicators:
  - 🟢 Green: Connected and responding
  - 🟡 Yellow: Connecting or uncertain state
  - 🔴 Red: Disconnected or error
  - ⚪ Gray: Not yet connected
- Device name and identifying information displayed

**Interaction:**
- **Single Click:** Select device (connects automatically)
- **Status Update:** Icon updates in real-time based on connection health

#### 3. Status Indicators

| Icon | Color | Status | Meaning |
|------|-------|--------|---------|
| ● | Green | Connected | Device responding normally |
| ● | Yellow | Connecting | Connection in progress |
| ● | Red | Error | Connection failed or device not responding |
| ● | Gray | Disconnected | No active connection |

### Behavior

**Device Selection:**
1. User clicks device in list
2. Application creates UDP worker thread
3. Connection established to device IP:port
4. Status icon updates to reflect connection state
5. Message Creator Panel populates with device commands
6. Status Panel cleared for new device context

**Device Deselection:**
- Occurs when selecting different device or closing connection
- UDP thread terminated gracefully
- Message Creator and Status Panel cleared
- Previous device state saved if configured

---

## Message Creator Panel

**Location:** Center column of Interactive Frame  
**File:** `core/workers/capstanDrive/message_creator_panel.py`

### Purpose

Provides intelligent, context-aware interface for constructing device commands with parameter validation.

### Key Features

- **Hierarchical Command Menu:** Commands organized by functional category
- **Dynamic Parameter Display:** Up to 10 parameters, shown only when relevant
- **Real-Time Message Assembly:** Command preview updates as parameters change
- **Type Validation:** Enforces correct parameter types and ranges
- **Conditional Parameters:** Shows/hides parameters based on previous selections
- **Enum Dropdowns:** Controlled input for enumerated options
- **Unit Display:** Parameter units shown for clarity

### Components

#### 1. Command Selection Button

**Appearance:** Dropdown button labeled "Select Command..."

**Behavior:**
- Click to open hierarchical menu
- Menu organized by categories:
  - Device Control
  - Device Status
  - Error Handling
  - System Administration
- Selected command name replaces button label
- Categories defined in command dictionary

**Menu Structure:**
```
Select Command ▼
  ├── Device Control
  │   ├── ENCODER
  │   ├── HPL
  │   ├── LED
  │   └── STEPPER
  ├── Device Status
  │   ├── GET_ALL
  │   ├── GET_ENCODER
  │   ├── GET_HPL
  │   ├── GET_LED
  │   └── GET_STEPPER
  ├── Error Handling
  │   ├── CLEAR_DEBUG_LOG
  │   ├── CLEAR_ERROR_LOG
  │   ├── CLR_WARN
  │   ├── GET_DEBUG_LOG
  │   └── GET_ERROR_LOG
  └── System Administration
      ├── GET_TIME_STATUS
      └── SET_TIME
```

#### 2. Instance Dropdown

**Purpose:** Select specific device instance (e.g., which LED)

**Behavior:**
- Appears below command selection
- Populated based on command dictionary configuration
- Shows relevant instances for selected command
- Hidden for commands without instance parameter
- Instance becomes first parameter in message

**Example:**
```
Command: LED
Instance: redLED | greenLED | blueLED
```

#### 3. Parameter Rows (10 maximum)

**Layout:** Each parameter row contains:
- Label (left): Parameter name with number
- Dropdown (center): For enum/boolean types
- Text input (center): For integer/float/string types
- Unit label (right): Units of measurement

**Parameter Types:**

1. **Enum Parameters:**
   - Dropdown with predefined options
   - Options from command dictionary
   - Selection index used in message

2. **Boolean Parameters:**
   - Dropdown with "On/Off" or "True/False"
   - Converted to 1/0 in message

3. **Integer Parameters:**
   - Text input field
   - Range validation applied
   - Minimum/maximum values enforced

4. **Float Parameters:**
   - Text input with decimal support
   - Precision validation
   - Range checking

5. **String Parameters:**
   - Free-form text input
   - Character limit validation if specified

**Conditional Display:**
- Parameters shown only when conditions met
- Example: "blink_count" shown only when mode=blink
- Conditions defined in command dictionary
- Dynamic show/hide as selections change

#### 4. Message Output Display

**Purpose:** Show assembled command string in real-time

**Features:**
- Read-only text field
- Updates immediately as parameters change
- Shows exact command that will be sent
- Provides feedback before transmission
- Validation errors prevent display update

**Format:**
```
COMMAND,param1,param2,param3,...
```

**Example:**
```
LED,redLED,blink,5,500
```
(LED command, red LED, blink mode, 5 blinks, 500ms duration)

### Workflow

1. **Select Command:** Click button → choose from hierarchical menu
2. **Choose Instance:** Select from dropdown (if applicable)
3. **Set Parameters:** Fill in required and optional parameters
4. **Review Message:** Check assembled command in output display
5. **Send Command:** Click SEND button in right panel

### Parameter Validation

**Pre-Send Validation:**
- Required parameters must be filled
- Values must be within specified ranges
- Type checking enforced
- Invalid entries highlighted
- Send button disabled until valid

**Validation Feedback:**
- Red border on invalid fields
- Tooltip shows error reason
- Message output clears on validation failure

---

## Status Panel

**Location:** Entire Status Frame (middle tier)  
**File:** `app/ui/status_panel.py`

### Purpose

Provides flexible status display supporting tabular data, text messages, and multimedia content including video playback.

### Display Modes

The Status Panel operates in two switchable modes, selectable via buttons at top of panel:

#### Mode 1: Table View

**Purpose:** Display structured device status information

**Features:**
- Two-column table: Item Name | Item Data
- Sortable columns
- Alternating row colors for readability
- Scrollable for large datasets
- Read-only display

**Usage:**
```python
# Update table with dictionary
main_window.update_status_table({
    'Device': 'CapstanDrive',
    'Status': 'Running',
    'Uptime': '12:34:56',
    'Temperature': '45°C',
    'LED Status': 'Green ON'
})
```

**Table Example:**

| Item Name | Item Data |
|-----------|-----------|
| Device | CapstanDrive |
| Status | Running |
| Uptime | 12:34:56 |
| Temperature | 45°C |
| LED Status | Green ON |

#### Mode 2: Text + Image/Video View

**Purpose:** Display status text alongside visual content

**Layout:** Horizontal split (50/50)

**Left Side - Text Box:**
- Plain text or rich text display
- Read-only
- Scrollable
- Timestamped messages
- Device logs or status updates

**Right Side - Media Display:**
- **Images:** PNG, JPG, BMP, GIF
  - Aspect ratio preserved
  - Scaled to fit frame height
  - Centered display
- **Videos:** MP4, AVI, MOV, MKV
  - Hardware-accelerated playback
  - Full playback controls (see below)
  - Aspect ratio maintained
- **Network Streams:** HTTP/HTTPS/RTSP URLs
  - Basic support in current version
  - Enhanced support planned for Pi 4B phase

### Video Playback Controls

**Control Bar Components:**

| Control | Icon | Function |
|---------|------|----------|
| Play | ▶ | Start or resume playback |
| Pause | ⏸ | Pause at current position |
| Stop | ⏹ | Stop and reset to beginning |
| Timeline | ──●── | Seek to any position (draggable) |
| Time Display | 01:23 / 04:56 | Current time / Total duration |

**Playback Features:**
- Click timeline to jump to specific position
- Drag timeline slider for precise seeking
- Time updates in real-time during playback
- Audio supported if present in video file
- Volume control (system level)

**Video API Usage:**
```python
# Load and play local video
main_window.update_status_video('C:/videos/tutorial.mp4')
main_window.control_video('play')

# Load network stream
main_window.update_status_video('http://192.168.1.100/stream.m3u8')

# Control playback
main_window.control_video('pause')
main_window.control_video('stop')

# Switch back to image
main_window.update_status_image('device_diagram.png')
```

### Mode Switching

**Buttons:** Located at top of Status Panel
- "Table View" button
- "Text + Image View" button

**Behavior:**
- Active mode button shown in bold
- Instant switching between modes
- Content preserved during switch
- Independent content for each mode

### Status Panel API

**Table Operations:**
```python
# Update entire table
status_panel.update_table({'key': 'value', ...})

# Add single row
status_panel.add_table_row('Item Name', 'Item Data')

# Clear table
status_panel.clear_table()
```

**Text Operations:**
```python
# Set text (replaces all)
status_panel.set_text('Status message')

# Append text (adds to end)
status_panel.append_text('New message')

# Clear text
status_panel.clear_text()
```

**Media Operations:**
```python
# Set image
status_panel.set_image('path/to/image.png')

# Set video (local file)
status_panel.set_video('path/to/video.mp4')

# Set video(network stream)
status_panel.set_video('http://url/stream', is_stream=True)

# Control playback
status_panel.play_video()
status_panel.pause_video()
status_panel.stop_video()

# Clear media
status_panel.clear_image()
status_panel.clear_video()
```

---

## Send/Reply Panel

**Location:** Right column of Interactive Frame  
**Width:** 200px (fixed)

### Purpose

Provides command transmission control and displays request/response information.

### Components

#### 1. SEND Button

**Appearance:** Prominent button at top of panel
**Size:** 80 x 40 pixels
**Function:** Transmit assembled command to device

**Behavior:**
- Click to send current command from Message Creator
- Blocked if any required parameter contains `□` (fill in all fields first)
- Click triggers:
  - Command sent via UDP
  - Request box updated
  - Reply box cleared (awaiting response)
  - ABORT timer started
  - Log entry created

#### 2. ABORT Button

**Appearance:** Red button next to SEND
**Size:** 80 x 40 pixels
**Function:** Cancel a pending command and clear the reply box

**Behavior:**
- Disabled by default
- Enables 1.5 seconds after SEND (prevents accidental clicks)
- Auto-disables if a reply arrives before the timer fires
- Click logs `[ABORTED]`, clears reply box, disables button

#### 3. Request Box

**Purpose:** Display most recently sent command

**Features:**
- Read-only text display
- Fixed height: 50px (approx 2 lines of text)
- Shows last sent command with "Sent:" prefix
- Scrollable if command length exceeds width
- Background color: Light yellow (#fffbe6)

**Format:**
```
Sent: COMMAND,param1,param2,...
```

**Example:**
```
Sent: LED,redLED,blink,5,500
```

#### 4. Reply Box

**Purpose:** Display device response to sent command

**Features:**
- Read-only text display
- Height: Dynamic (fills remaining space in column)
- Scrollable for long responses
- Background color: Light blue (#e6f7ff)
- Auto-clears when new command sent
- Auto-scrolls to show latest content

**Content Types:**
- Success messages
- Error responses
- Device status information
- Multi-line responses supported

**Example Responses:**
```
capstanDrive: OK

capstanDrive: ERROR invalid parameter

capstanDrive: STEPPER,running,1000,forward
```

### User Interaction Flow

1. User creates command in Message Creator Panel
2. User reviews assembled message
3. User clicks SEND button
4. Request box shows sent command
5. Reply box clears; ABORT button arms after 1.5s
6. Device response appears in reply box; ABORT disarms
7. Log panel records transaction

---

## Logging Panel

**Location:** Bottom tier (Logging Frame)  
**Height:** 200px (fixed)

### Purpose

Provides comprehensive logging of all application and network activities for debugging and audit trails.

### Features

- **Read-Only Display:** Prevents accidental editing
- **Auto-Scroll:** Automatically shows latest messages
- **Timestamped Entries:** Each log line prefixed with timestamp
- **Color Coding:** Different message types in different colors (if enabled)
- **Scrollable History:** Access previous messages via scrollbar
- **Persistent Log:** Log preserved during session

### Log Entry Types

#### System Messages

**Format:** `[SYSTEM] message`

**Examples:**
```
[SYSTEM] Application started
[SYSTEM] Loading server configuration
[SYSTEM] 5 devices found in configuration
```

#### Network Messages

**Format:** `[UDP] message`

**Examples:**
```
[UDP] Connecting to 192.168.1.100:5555...
[UDP] Connected successfully (local port 54321)
[UDP] Sent: LED,redLED,on
[UDP] From capstanDrive: OK
[UDP] Connection closed
```

#### Error Messages

**Format:** `[ERROR] message`

**Examples:**
```
[ERROR] Failed to connect to device
[ERROR] Invalid parameter value: expected integer
[ERROR] Timeout waiting for response
```

#### UI Messages

**Format:** `[UI] message`

**Examples:**
```
[UI] Selected server: CapstanDrive (192.168.1.100:5555)
[UI] Command menu populated with 16 commands
[UI] Device deselected
```

### Log Management

**Capacity:** Last 1000 messages retained (configurable)
**Overflow:** Oldest messages discarded when limit reached
**Export:** Copy log contents to clipboard (right-click menu)
**Clear:** Clear log button in menu bar (optional)

---

## UI Customization

### Configuration File

UI dimensions and styling controlled in `config.py`:

```python
# Window Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 800

# Frame Heights
LOGGING_FRAME_HEIGHT = 200
STATUS_FRAME_HEIGHT = 350
INTERACTIVE_FRAME_HEIGHT = 350

# Panel Widths
DEVICE_PANEL_WIDTH = 200
DROPDOWN_WIDTH = 250
LABEL_WIDTH = 85

# Component Sizes
MESSAGE_OUTPUT_HEIGHT = 25
REQUEST_BOX_HEIGHT = 50
SEND_BUTTON_WIDTH = 80
SEND_BUTTON_HEIGHT = 40

# Spacing
VERTICAL_SPACING = 2
HORIZONTAL_SPACING = 4
```

### Modifying Layout

**Resize Frames:**
1. Edit height constants in `config.py`
2. Ensure total height ≤ WINDOW_HEIGHT
3. Restart application

**Resize Panels:**
1. Edit width constants
2. Consider minimum widths for content
3. Test with various resolutions

### Custom Styling

**Qt StyleSheets:**
- Styles defined inline or in external .qss files
- Apply to individual widgets or globally
- Support CSS-like syntax

**Example:**
```python
widget.setStyleSheet("background: #f0f0f0; border: 1px solid #ccc;")
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Send command (same as SEND button) |
| Ctrl+L | Clear log panel |
| Ctrl+D | Disconnect current device |
| Ctrl+Q | Quit application |
| F5 | Refresh device list |
| Esc | Clear message creator selections |

---

## Troubleshooting

### Issue: Command button menu empty

**Cause:** Command dictionary not loaded or malformed
**Solution:** 
1. Check `shared_dictionaries/command_dictionaries/` folder
2. Verify JSON syntax in command dictionary file
3. Check application log for loading errors

### Issue: Parameters not showing

**Cause:** Conditional parameter requirements not met
**Solution:**
1. Check prerequisite parameter selections
2. Review command dictionary conditions
3. Ensure enum values match expected strings

### Issue: Video not playing

**Cause:** Codec not supported or file corrupted
**Solution:**
1. Verify video file opens in media player
2. Check file format (MP4/H.264 recommended)
3. Install Qt Multimedia codecs if needed
4. Check application log for media errors

### Issue: Status panel not updating

**Cause:** Display mode mismatch or API not called
**Solution:**
1. Verify correct mode selected (Table vs Split)
2. Check that handler calls status update methods
3. Review signal/slot connections in code

### Issue: Reply box shows nothing

**Cause:** Device not responding or UDP port mismatch
**Solution:**
1. Check device network connectivity
2. Verify device IP and port configuration
3. Review log panel for UDP errors
4. Ensure device replies to correct source port

---

## Related Documentation

- **Architecture:** See `architecture.md` for system design
- **Status Panel Details:** See `status_panel_guide.md` for multimedia features
- **Command Menu System:** See `command_menu_system.md` for menu customization
- **Usage Guide:** See `usage.md` for basic operations
- **API Reference:** See source code documentation for detailed API

---

**For PDF Generation:** This document is formatted for professional PDF output. See `pdf_generation_guide.md` for conversion instructions.
