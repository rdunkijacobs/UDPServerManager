# Usage Guide: UDP Server Manager

**Document Version:** 2.0  
**Last Updated:** February 19, 2026  
**Application Version:** UDP Server Manager v2.0+

---

## Table of Contents
- [Quick Start](#quick-start)
- [Application Overview](#application-overview)
- [Working with Devices](#working-with-devices)
- [Command Menu System](#command-menu-system)
- [Message Creation](#message-creation)
- [Status Panel](#status-panel)
- [Video Playback](#video-playback)
- [UDP Networking](#udp-networking)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)

---

## Quick Start

### Installation

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Configuration:**
   - Check `data/servers.json` for device configurations
   - Ensure UDP ports are not blocked by firewall

3. **Start Application:**
   ```bash
   python main.py
   ```

### First Steps

1. **Select Device:** Click device panel on left (200px width)
2. **Choose Command:** Click "SELECT COMMAND" button → choose category → select command
3. **Configure Parameters:** Fill in up to 10 parameters as needed
4. **Send Message:** Click "SEND MESSAGE" button on right
5. **View Response:** Check logging panel at bottom (200px height)

---

## Application Overview

### Main Window Layout

The application uses a **three-tier layout**:

**Top Tier - Interactive Area (350px height):**
- **Left:** Device Panel (200px) - Select active device
- **Center:** Message Creator Panel - Build commands with hierarchical menu
- **Right:** Send/Reply Panel - Execute commands and view replies

**Middle Tier - Status Area (350px height):**
- Status Panel with dual modes:
  - **Table Mode:** Display device status data in structured table
  - **Split Mode:** Text display + image/video playback area

**Bottom Tier - Logging Area (200px height):**
- Real-time UDP traffic logging
- Sent messages and received responses
- Error messages and warnings

### Window Management

- **Automatic Positioning:** Window position saved on close
- **Size Persistence:** Window dimensions restored on launch
- **Last Device Memory:** Previously selected device auto-selected
- **Preferences:** Stored in user config file

---

## Working with Devices

### Device Selection

**Device Panel (Left Side):**
1. Click any device name to make it active
2. Active device highlighted with visual feedback
3. Message creator updates to show device-specific commands
4. Status panel can display device state information

### Adding New Devices

**Edit `data/servers.json`:**
```json
{
  "servers": [
    {
      "name": "My New Device",
      "ip": "192.168.1.100",
      "port": 5000,
      "worker_type": "capstan_drive"
    }
  ]
}
```

**Required Fields:**
- `name`: Display name for device
- `ip`: Device IP address
- `port`: UDP port number
- `worker_type`: Worker class to handle communication

**Restart Application:** Changes take effect after restart.

### Device Configuration Files

Each device type has configuration in `core/workers/[device_type]/`:
- `[device]_config.py` - Device-specific settings
- `[device]_commandDictionary.json` - Available commands
- `[device]_handler.py` - Message handling logic
- `[device]_worker.py` - Network communication thread

---

## Command Menu System

### Hierarchical Menu Structure

**NEW in v2.0:** Commands organized in **flyout menus** by category.

**Access Command Menu:**
1. Click **"SELECT COMMAND"** button in message creator panel
2. Hover over category to reveal submenu
3. Click command to select it

**Default Categories:**
- **Device Control** - Commands that control device hardware
- **Device Status** - Commands that query device state
- **Error Handling** - Commands for error logs and diagnostics
- **System Administration** - Commands for device configuration

### Category Examples

**Device Control Category:**
- LED - Control LED states
- HPL - High Power Laser operations
- STEPPER - Stepper motor control
- ENCODER - Encoder readings

**Device Status Category:**
- GET_LED - Query LED status
- GET_HPL - Query laser status
- GET_STEPPER - Query motor position
- GET_ENCODER - Query encoder value
- GET_ALL - Query all device parameters

**Error Handling Category:**
- CLR_WARN - Clear warning flags
- GET_ERROR_LOG - Retrieve error log
- GET_DEBUG_LOG - Retrieve debug log
- CLEAR_ERROR_LOG - Erase error log
- CLEAR_DEBUG_LOG - Erase debug log

**System Administration Category:**
- SET_TIME - Set device clock
- GET_TIME_STATUS - Query device time sync status

### Command Selection Workflow

1. **Click "SELECT COMMAND" button**
   - Button displays current selection or "SELECT COMMAND"
   
2. **Choose Category**
   - Hover over category (e.g., "Device Control")
   - Submenu flies out to the right
   
3. **Select Command**
   - Click desired command (e.g., "LED")
   - Menu closes automatically
   - Button updates to show selected command
   
4. **Configure Parameters**
   - Parameter fields appear below command button
   - Number of fields depends on command (0-10 parameters)
   
5. **Send Message**
   - Click "SEND MESSAGE" button on right
   - Message sent to active device

**See Also:** `command_menu_system.md` for detailed customization guide.

---

## Message Creation

### Message Creator Panel (Center)

**Command Selection:**
- Click **"SELECT COMMAND"** → category → command
- Selected command appears on button label

**Parameter Configuration:**
- Up to **10 parameters** supported (expanded from 8)
- Parameter types:
  - **Enum:** Dropdown menu (e.g., LED_MODE: OFF, ON, BLINK)
  - **Boolean:** Dropdown with TRUE/FALSE (sent as 1/0)
  - **Integer:** Text input with validation
  - **Float:** Text input with decimal support
  - **String:** Text input for alphanumeric data

**Conditional Parameter Display:**
- Some parameters only visible when certain modes selected
- Example: BLINK_RATE only shown when LED_MODE is BLINK
- Irrelevant parameters hidden automatically

**Real-Time Message Preview:**
- Message string assembled dynamically
- Shown in preview area (if enabled)
- Format: `COMMAND:param1:param2:param3...`

### Parameter Validation

**Automatic Checks:**
- **Integer Range:** Min/max enforcement from command dictionary
- **Float Precision:** Decimal places validated
- **String Length:** Maximum character limits
- **Enum Values:** Only valid options selectable
- **Required Fields:** Cannot send until all required params filled

**Visual Feedback:**
- Invalid entries highlighted in red
- Tooltip shows error message
- Send button disabled until all fields valid

---

## Status Panel

### Overview

The **Status Panel** (middle tier, 350px height) displays device state and multimedia content.

### Table Mode

**Purpose:** Display structured device status data.

**Usage:**
1. Device sends status update message
2. Handler parses data into key-value pairs
3. Status panel populates table automatically

**Table Layout:**
- **Column 1:** Parameter name (e.g., "LED Status")
- **Column 2:** Current value (e.g., "ON")
- Auto-sizing columns for optimal readability

**Example Status Data:**
```
LED Status:    ON
HPL Status:    OFF
Motor Position: 1250
Encoder Value: 3456
Temperature:   42.5°C
```

### Split Mode

**Purpose:** Display text information alongside images or video.

**Layout:**
- **Left Side (40%):** Text display area for status messages
- **Right Side (60%):** Image or video player

**Usage:**
1. Send status query command to device
2. Device responds with status text
3. Text displayed in left pane
4. Optional: Load image/video to right pane

**Text Display Features:**
- Automatic word wrap
- Scroll bar for long content
- Monospace font option for tabular data
- Copy-to-clipboard functionality

---

## Video Playback

### Overview

**NEW in v2.0:** Status panel supports video playback with full controls.

### Supported Formats

**Video Files:**
- MP4 (H.264 codec recommended)
- AVI
- MOV
- MKV

**Network Streams:**
- HTTP/HTTPS URLs
- RTSP streams (basic support)
- **Future:** Live streams from Raspberry Pi 4B cameras

### Loading Video

**Local File:**
```python
# In application code
status_panel.set_video("path/to/video.mp4", is_stream=False)
```

**Network Stream:**
```python
# In application code
status_panel.set_video("http://example.com/stream", is_stream=True)
```

### Playback Controls

**Control Bar Components:**
- **Play Button:** Start playback
- **Pause Button:** Pause (retains position)
- **Stop Button:** Stop and reset to beginning
- **Timeline Slider:** Seek to specific time
- **Time Display:** Current time / Total duration (MM:SS format)

**Keyboard Shortcuts:**
- `Space` - Play/Pause toggle
- `S` - Stop
- `← →` - Skip backward/forward 5 seconds
- `[ ]` - Adjust playback speed

**Mouse Controls:**
- **Click Timeline:** Jump to position
- **Drag Timeline:** Scrub through video
- **Double-Click Video:** Toggle fullscreen (future feature)

### Video Use Cases

1. **Device Inspection:** View camera feed from inspection cameras
2. **Process Monitoring:** Display live manufacturing process
3. **Maintenance Guides:** Show instructional videos
4. **Status Visualization:** Animated device status diagrams
5. **Recorded Footage:** Review historical camera recordings

---

## UDP Networking

### Network Architecture

**Single UDP Socket Design:**
- One UDP socket handles both sending and receiving
- All outgoing messages use same local port as receive thread
- Device responses automatically routed to receive thread
- Eliminates port conflicts and socket management issues

### Message Flow

1. **User Action:** Select command, fill parameters, click "SEND MESSAGE"
2. **Message Assembly:** Handler formats command string
3. **UDP Transmission:** Message sent to device IP:port
4. **Device Processing:** Device receives, processes, responds
5. **Response Reception:** Supervisor receives response on same socket
6. **Handler Processing:** Response parsed and displayed
7. **Logging:** Both sent message and response logged

### UDP Configuration

**Default Settings:**
- **Local Port:** Auto-assigned by OS (ephemeral port range)
- **Timeout:** 5 seconds for response
- **Retries:** 0 (no automatic retries)
- **Buffer Size:** 4096 bytes

**Custom Configuration** (`config.py`):
```python
UDP_TIMEOUT = 5.0  # seconds
UDP_BUFFER_SIZE = 4096  # bytes
UDP_ENABLE_BROADCAST = False  # broadcast messages
```

### Firewall Configuration

**Windows Firewall:**
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Inbound Rules → New Rule
4. Rule Type: Port
5. Protocol: UDP, Specific local ports: [your port]
6. Action: Allow the connection
7. Profile: All profiles
8. Name: "UDP Server Manager"

**Testing Connectivity:**
```bash
# Test UDP port open
Test-NetConnection -ComputerName [device_ip] -Port [port] -InformationLevel Detailed
```

---

## Troubleshooting

### Common Issues

#### Issue: Command Menu Not Appearing

**Symptoms:** Clicking "SELECT COMMAND" button does nothing

**Possible Causes:**
- Command dictionary file missing or corrupted
- JSON syntax error in command dictionary
- Categories array empty or malformed

**Solutions:**
1. Verify `[device]_commandDictionary.json` exists
2. Validate JSON syntax: `python -m json.tool [file].json`
3. Check "categories" array is populated
4. Ensure all commands have "category" field

#### Issue: Parameters Not Showing

**Symptoms:** No parameter fields appear after selecting command

**Possible Causes:**
- Command has no parameters defined
- Command definition missing "parameters" array
- Conditional logic hiding all parameters

**Solutions:**
1. Check command dictionary for "parameters" array
2. Verify parameter definitions include required fields
3. Review conditional display logic in handler code

#### Issue: Video Not Playing

**Symptoms:** Video area blank or shows error message

**Possible Causes:**
- Video file not found or path incorrect
- Unsupported codec (not H.264)
- Missing Qt Multimedia dependencies
- Network stream URL unreachable

**Solutions:**
1. Verify file path is absolute and file exists
2. Convert video to H.264 codec: `ffmpeg -i input.mp4 -c:v libx264 output.mp4`
3. Reinstall PySide6: `pip install --upgrade PySide6`
4. Test stream URL in VLC media player first
5. Check firewall not blocking stream

#### Issue: "No Response from Device"

**Symptoms:** Message sent but no reply received

**Possible Causes:**
- Device offline or not on network
- Firewall blocking UDP traffic
- Device replying to wrong port
- Device response time exceeds timeout

**Solutions:**
1. Ping device: `ping [device_ip]`
2. Check device is powered on and connected
3. Verify firewall allows UDP on device port
4. Increase timeout in `config.py`: `UDP_TIMEOUT = 10.0`
5. Check device logs for received messages
6. Verify device replies to source port of incoming message

#### Issue: Status Panel Not Updating

**Symptoms:** Status panel shows stale data

**Possible Causes:**
- Handler not calling update method
- Response parsing returning empty data
- Status panel in wrong mode for data type

**Solutions:**
1. Add debug logging to handler: `print(f"Status data: {data}")`
2. Verify response parsing logic correctness
3. Check status panel mode matches data type (table vs split)
4. Call `gui.update_status_table(data_dict)` explicitly

### Debugging Tips

**Enable Verbose Logging:**
```python
# In config.py
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
```

**Network Traffic Capture:**
```bash
# Use Wireshark to capture UDP packets
# Filter: udp.port == [your_port]
```

**Command Line Testing:**
```python
# Test message formatting without GUI
python -c "from core.workers.capstanDrive.capstanDrive_handler import *; \
           print(format_message('LED', ['1', '500']))"
```

### Error Messages

**"Command dictionary not found"**
- Missing JSON file in worker directory
- Check path: `core/workers/[device]/[device]_commandDictionary.json`

**"Invalid parameter count"**
- Sent parameters don't match command definition
- Review command dictionary for correct parameter count

**"Network timeout"**
- Device didn't respond within timeout period
- Increase `UDP_TIMEOUT` or check device connectivity

**"Video codec not supported"**
- Video file uses unsupported codec
- Convert to H.264: `ffmpeg -i input.mp4 -c:v libx264 output.mp4`

---

## Advanced Features

### Custom Command Dictionaries

**Creating New Commands:**
1. Edit `[device]_commandDictionary.json`
2. Add command to "categories" array if new category
3. Add command definition:
   ```json
   {
     "name": "MY_COMMAND",
     "category": "Device Control",
     "description": "Does something useful",
     "parameters": [
       {
         "name": "param1",
         "type": "integer",
         "min": 0,
         "max": 100
       }
     ]
   }
   ```
4. Implement handler in `[device]_handler.py`
5. Restart application

**See Also:** `command_dictionary_tutorial.md` for detailed guide.

### Multi-Device Coordination

**Send Command to Multiple Devices:**
```python
# In custom script
for device_name in ["Device1", "Device2", "Device3"]:
    select_device(device_name)
    send_command("LED", ["1", "1000"])
    time.sleep(0.1)  # Small delay between devices
```

### Batch Command Execution

**Future Feature:** Macro system for command sequences.

**Current Workaround:** Python script automation.

---

## Keyboard Shortcuts

### Global

- `Ctrl+Q` - Quit application
- `Ctrl+R` - Refresh device list
- `F5` - Reconnect to active device

### Message Creator

- `Enter` - Send message (when all parameters valid)
- `Esc` - Clear parameter fields
- `Tab` - Move to next parameter field

### Video Playback

- `Space` - Play/Pause
- `S` - Stop
- `← →` - Seek backward/forward 5 seconds

---

## Related Documentation

- **Architecture:** See [architecture.md](architecture.md) for system design
- **UI Components:** See [ui_components_guide.md](ui_components_guide.md) for detailed UI reference
- **Command Menu:** See [command_menu_system.md](command_menu_system.md) for menu customization
- **Message Creator:** See [message_creator_panel.md](message_creator_panel.md) for advanced features
- **PDF Generation:** See [pdf_generation_guide.md](pdf_generation_guide.md) for documentation export

---

## Support

- **Project Maintainer:** Contact via project repository
- **Issue Tracking:** Open issues in version control system
- **Documentation:** All guides in `docs/` directory
- **Contributing:** See [contributing.md](contributing.md) for development guidelines

---

## Advanced Markdown Features

- [x] Tables
- [x] Task Lists
- [x] Syntax-highlighted code blocks
- [x] Mermaid diagrams
- [x] Footnotes
- [x] Images
- [x] Links
- [x] Blockquotes
- [x] Math (KaTeX/LaTeX)

See `markdown_features_demo.md` for examples.

---
