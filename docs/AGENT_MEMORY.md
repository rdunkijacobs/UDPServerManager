# Agent Memory — UDPServerManager

This file is read at the start of each session to restore context. Update it whenever something important is learned or decided.

---

## Communication Style

- **Always explicitly confirm what was changed and what was not.**
- User is on Claude Sonnet 4.6 (was 4.5).
- User is working on **three active projects**, two more coming — all share this codebase pattern.

## Design Philosophy

- **Short. Clear. Pithy.** Eliminate every word, pixel, and byte that isn't earning its place.
- **Occam's Razor:** the simplest solution that fully solves the problem is the right one.
- **Operator overload is real.** Never show a technician more than they need right now.
- **Push back when something doesn't add up.** Don't just implement a questionable idea — flag the concern, give reasons, work it out together. The user appreciates being challenged.

---

## Project Overview

**UDP Server Manager v2.01** — Windows 10/11 desktop app (Python 3, PySide6/Qt).

### Role in the System
- This app is the **Supervisor** — administrative/monitoring only, makes no control decisions.
- Sits between edge devices (Pico/xiRTOS, Raspberry Pi 4B, AS-410M) and a higher-level **SpoolerController** (HMI).
- SpoolerController sends control directives directly to edge server threads; Supervisor only monitors/displays.

### Key Files
| File | Purpose |
|------|---------|
| `main.py` | Entry point; loads `data/servers.json`, creates `MainWindow` |
| `config.py` | All UI dimensions, version (2.01), health monitoring settings |
| `data/servers.json` | Server locations/IPs/ports grouped by location (xiTechnology, ANZA, DNS, Local) |
| `core/udp.py` | UDP networking engine (`UDPClientThread`) |
| `app/ui/gui.py` | Main window, 3-tier layout |
| `app/ui/device_panel.py` | Left panel — device selection |
| `app/ui/status_panel.py` | Middle panel — table/split mode, video playback — **built for Pi 4B** |
| `core/workers/capstanDrive/` | Device-specific worker, handler, config, command dict, message creator |

### UI Layout
- **Top (350px):** Interactive — Device Panel (left 200px) | Message Creator (center) | Send/Reply (right)
- **Middle (350px):** Status Panel — Table Mode or Split Mode (text + media)
- **Bottom (200px):** Logging

### Worker/Handler Pattern (per device type)
```
core/workers/deviceType/
├── deviceType_worker.py
├── deviceType_handler.py
├── deviceType_config.py
├── deviceType_commandDictionary.json   ← ALL commands defined here
└── message_creator_panel.py            ← UI for building messages
```

---

## Command Dictionary System

**Location:** `core/workers/capstanDrive/capstanDrive_commandDictionary.json`

All inter-processor commands are 100% defined in the JSON command dictionary. No hardcoded command lists anywhere.

### Current Commands (CapstanDrive)
| Command | Category | Param 1 Type | Notes |
|---------|----------|-------------|-------|
| LED | Device Control | enum (led_number: redLED/greenLED/blueLED) | Multi-mode: on_off/toggle/blink/flash |
| HPL | Device Control | integer (hpl_number 1-1) | High power logic output |
| STEPPER | Device Control | enum (motor_number: DVR8833/DVR882X/HighPower) | 12 modes, up to 9 params |
| ENCODER | Device Control | enum (encoder_number: A/B) | reset/arm/disarm/position |
| GET_LED | Device Status | integer (1-8) | Returns state/mode/mode_params |
| GET_HPL | Device Status | integer (1-4) | Returns state |
| GET_STEPPER | Device Status | integer (1-4) | Returns 11 fields |
| GET_ENCODER | Device Status | integer (1-2) | Returns position/index_armed |
| CLR_WARN | Error Handling | enum (motor_number: DVR8833/DVR882X/HighPower) | Clears warning by ID |
| GET_ERROR_LOG | Error Handling | enum (level_filter: ALL/FATAL/SEVERE/WARNING) | + limit param |
| GET_DEBUG_LOG | Error Handling | enum (level_filter: ALL/INFO/DEBUG) | + limit param |
| CLEAR_ERROR_LOG | Error Handling | enum (level_filter: ALL/FATAL/SEVERE/WARNING) | |
| CLEAR_DEBUG_LOG | Error Handling | enum (level_filter: ALL/INFO/DEBUG) | |
| GET_ALL | Device Status | none | Returns all shared states |
| GET_STATUS | Device Status | none | Returns uptime/cpu/memory/temperature |

### Parameter conventions
- `param_number` is 1-based in the JSON.
- If param 1 is `enum` type: shown as a regular dropdown in the UI (instance dropdown hidden).
- If param 1 is not `enum`: shown in the instance dropdown (named after the param).
- Enum options: `[{"value": "text", "tooltip": "..."}]` (new) or plain string array (legacy).
- Conditional params: `"condition": ["mode == blink"]` — shown only when parent param matches.
- Context-dependent units: `[{"tC": "s"}, {"rev": "rev"}]` list of dicts keyed by option value.

### CapstanDrive Config (`capstanDrive_config.py`)
- `BOOLEAN_CONFIG`: true_strings, false_strings, display_options, message_encoding (`["1","0"]`)
- `COMMAND_COUNTS`: instance names per command for instance dropdown
- `INSTANCE_MAP`, `MODE_MAP`: index-to-name mappings
- `DEFAULT_PORT`: 5005

### Servers (`data/servers.json`)
- Groups: `xiTechnology`, `ANZA`, `DNS`, `Local`
- Each server: `name`, `clientName` (maps to worker type), `host`, `port`, `description`
- `clientName: "capstanDrive"` → uses capstanDrive worker/handler/command dict
- Local test device: `127.0.0.1:5000`

---

## Full Managed Server Inventory (MZSpooler System)

### PICO2W-Based Servers (UDP, xiRTOS)
| Server | Role | Notes |
|--------|------|-------|
| TransferTapeBrake | Controls tape brake mechanism | |
| SpeedSensor (transfer) | Measures speed on transfer path | |
| SpeedSensor (transport) | Measures speed on transport path | |
| capstanDrive | Controls main capstan drive | Base implementation |
| frameControl | Controls frame positioning/mechanics | |
| pressurePlateControl | Controls pressure plate actuator | |
| transportSpoolDrive | Controls transport spool | **Inherits capstanDrive logic** |
| windowSpoolDrive | Controls window spool | **Inherits capstanDrive logic** |
| wasteSpoolDrive | Controls waste spool | **Inherits capstanDrive logic** |
| dancerController (input) | Controls input dancer mechanism | Identical code to waste dancer |
| dancerController (waste) | Controls waste dancer mechanism | Identical code to input dancer |

### Raspberry Pi 4B-Based Servers (TCP for images, compute-intensive)
| Server | Role |
|--------|------|
| QA Sensor | Quality assurance (image/AI tasks) |
| SamplePositionSensor | Detects/monitors sample position |
| FramePositionSensor | Detects/monitors frame position |
| FrameQASensor | Frame quality assurance |

### External Servers
| Server | Role | Notes |
|--------|------|-------|
| AS-410M | DNS coordination and sample metadata | Wired LAN, requires Firewall/VPN traversal |

### Critical Design Notes
- **capstanDrive code is reused by transportSpoolDrive, windowSpoolDrive, and wasteSpoolDrive** — any bug fix or change to the capstanDrive worker/handler/command dictionary affects 4 drives.
- Raspberry Pi 4B servers are **dual-protocol**:
  - **UDP** for commands (same pattern as all other devices)
  - **TCP/IP** for large file transfers (images, videos) — separate channel
- All Pico2W / xiRTOS devices use UDP only.
- The AS-410M requires special network handling (NAT traversal or VPN) — it is on a separate network.
- SpoolerController (HMI) communicates **directly** with edge server threads, never through the Supervisor for control directives.
- All edge server threads check the **shared emergency mailbox** first, then their own standard mailbox.

---

## Known Bugs Fixed

### 2026-02-22 — Enum param 1 index off-by-one (`message_creator_panel.py`)
- **Location:** `update_assembled_message()`, branch `elif param_type == 'enum' and param_num == 1`
- **Bug:** `currentIndex() - 1` was used, sending index 0 for the first option instead of 1.
- **Fix:** Changed to `currentIndex()` — placeholder is at index 0, so `currentIndex()` already gives the correct 1-based index.
- **Scope:** Generic fix — covers all commands with an enum param 1 (LED, STEPPER, ENCODER, CLR_WARN, GET_ERROR_LOG, GET_DEBUG_LOG, CLEAR_ERROR_LOG, CLEAR_DEBUG_LOG).
- **No other changes were made.**

---

## Conventions & Decisions

- Enum param 1 values sent in messages are **1-based indices** (placeholder at index 0 is never sent).
- Instance dropdown (non-enum param 1) also uses `currentIndex()` directly — same 1-based convention, confirmed correct.
- Message assembly uses text (not index) for all enum params **except param 1** — param 1 enums always send the index number.
- Boolean params encoded per `BOOLEAN_CONFIG.message_encoding` (`"1"` / `"0"`).
- Health monitoring is currently disabled (`HEALTH_CHECK_ENABLED = False` in `config.py`).
- Version: 2.01

---

## Message Protocol

- **Message format is CSV (comma-separated, no spaces):** `COMMAND,param1,param2,...`  
  Example: `LED,1,blink,5,500`  
  Built via `",".join(msg_parts)` in `update_assembled_message()`.
- The assembled message is shown live in `assembled_output` label before sending.
- Missing/unfilled required parameters shown as `□` placeholder in the preview.
- **Health check PING format:** `PING:timestamp:metric1,metric2,...`
- **Health check PONG format:** `PONG:timestamp:key=val,key=val,...`
- PING/PONG handled at highest priority on edge device — before regular commands.

---

## Numeric Input Handling (message_creator_panel.py)

All typed integer/float fields go through a rich input pipeline:

### What users can type
| Feature | Syntax | Converted to |
|---------|--------|-------------|
| Plain number | `3.14`, `-17`, `1000` | sent as-is |
| Thousands commas (display only) | `1,000`, `12,345,678` | commas stripped before send |
| Leading dot | `.5` → fixed to `0.5` | `0.5` |
| Leading dot negative | `-.5` → fixed to `-0.5` | `-0.5` |
| Scientific notation | `1.5e-3`, `2E+5` | sent as-is after comma strip |
| **Time suffixes** (units `s` params only) | `5ms`, `2.5us`, `100ns` | converted to seconds (Decimal precision) |
| **SI multipliers** (rev/deg params only) | `10m`→×0.001, `5k`/`5K`→×1000, `2.5M`→×1,000,000 | multiplied, Decimal precision |

### Comma validation rules (thousands separator)
- Only valid in integer part (before `.` or `e`)
- Cannot start or end with a comma
- First group: 1–3 digits; subsequent groups: exactly 3 digits
- Leading-zero groups disallowed: `0,001` is invalid (should be `0.001`)

### On invalid input (triggered at `editingFinished`)
- `QMessageBox.warning` shown with type description + examples + suffix hint
- Field flashes red 3× (200 ms per flash cycle)
- Focus and `selectAll()` returned to the bad field after flash

### Validation regex patterns (after comma removal)
- **integer:** `^[+-]?(\d+([eE][+-]?\d+)?)$`
- **float:** `^[+-]?(\d+\.?\d*|\d*\.\d+)([eE][+-]?\d+)?$`

### `_format_number_no_scientific()` helper
Used for time/SI conversions — applies a multiplier using `Decimal` arithmetic to avoid floating-point precision errors, then formats the result without scientific notation.

---


## Health Monitoring System (core/health_monitor.py)

Currently **disabled** (`HEALTH_CHECK_ENABLED = False` in `config.py`). Fully implemented and ready to enable.

### Key Config Values (`config.py`)
| Setting | Value | Meaning |
|---------|-------|---------|
| `HEALTH_CHECK_ENABLED` | `False` | Master on/off switch |
| `HEALTH_CHECK_INTERVAL_ms` | `10000` | Round-robin cycle interval |
| `PONG_TIMEOUT_ms` | `1000` | Max wait for PONG response |
| `FAILURE_WINDOW` (M) | `10` | Sliding window width |
| `FAILURE_THRESHOLD` (N) | `3` | Failures in window → FATAL |
| Slow response window | `10` | Checks for slow detection |
| Transit anomaly window | `18` | ~3-minute window at 10s cycle |

### HealthStatus Class (per-worker state tracker)
Three deques track history:
- `check_history` — maxlen=M (failure window), stores True/False per check
- `response_times` — maxlen=slow_window, stores round-trip times
- `transit_times` — maxlen=18 (~3-min window), stores transit times; **cleared on CRITICAL or FATAL**

Key fields:
- `previous_error_level` — used for state-transition detection
- `transit_anomaly_detected` — bool, set by `_check_transit_anomaly()`
- `negotiated_metrics` — list of metrics the device agreed to send
- `additional_info` — dict, extra data from PONG response

Key methods:
- `record_success(response_time)` — appends True to window, updates response_times/transit_times
- `record_failure()` — appends False to window, increments consecutive_failures
- `_update_status()` — computes current error level from window
- `_check_transit_anomaly()` — requires full 18-check window; uses `statistics.stdev`; flags if latest > mean + 2σ
- `get_status_dict()` — returns full dict for signal emission
- `get_tooltip_text()` — formatted string for UI tooltip

### Status Priority (evaluated in order)
1. **FATAL** — N or more failures in window of M checks
2. **CRITICAL** — last check failed (but not yet FATAL threshold)
3. **WARNING** — transit anomaly detected (stats.stdev check) **OR** slow response times
4. **HEALTHY** — all checks passed, no anomalies

Transit anomaly window is **cleared** when status becomes CRITICAL or FATAL (fresh baseline on recovery).

### HealthMonitor(QObject) Signals
```python
health_status_updated = Signal(str, dict)       # server_name, status_dict — every cycle
health_warning        = Signal(str, str)         # server_name, message
health_critical       = Signal(str, str)         # server_name, message
health_fatal          = Signal(str, str)         # server_name, message
escalate_to_controller = Signal(str, dict)       # server_name, status_dict
round_robin_cycle_complete = Signal(float)       # cycle_duration_ms
round_robin_timing_warning = Signal(float, float) # actual_ms, expected_ms
```

**Signal/escalation emission is on state transitions only** (`previous_error_level != error_level`). `health_status_updated` fires every cycle regardless.

### PING Timestamp Logic
- **PING without timestamp** (`"PING"`) — normal round-robin checks (minimal overhead, 4 bytes)
- **PING with timestamp** (`"PING:yyyymmdd.HHMMSS.xxx"`) — sent only on:
  1. First contact (status was UNKNOWN)
  2. Recovery from FATAL or CRITICAL
- Timeout uses `QTimer.singleShot(PONG_TIMEOUT_ms, lambda: _check_timeout(...))`

### Worker Requirements (UDPClientThread)
Workers registered with HealthMonitor must expose:
- `pong_received` signal: `Signal(str, float, dict)` — `(worker_name, ping_time, additional_info)`
- `send_ping(ping_time, send_timestamp=False)` method

`UDPClientThread` in `core/udp.py` implements both. It intercepts PONG in `run()` loop **before** normal command dispatch and calls `_handle_pong_message()`. Pending pings tracked in `self.pending_pings` dict keyed by tracking key (timestamp string or `"PING"`).

### GUI Integration (app/ui/gui.py)
- `handle_device_selected()` → `health_monitor.register_worker(server_name, udp_thread, requested_metrics)`; starts timer if not running
- `handle_device_deselected()` → `health_monitor.unregister_all_workers()`; stops timer
- `_on_health_status_updated()` → checks `device_health_history` for first-contact and post-FATAL recovery → sends ZULU sync; updates device panel icon; logs non-OK status
- `_on_health_critical()` / `_on_health_fatal()` → `QMessageBox.Warning` / `QMessageBox.Critical` dialog
- `_on_escalate_to_controller()` → log only (future: notify SpoolerController)
- `_on_manual_health_check()` → `health_monitor.trigger_manual_check()`
- `_on_hourly_zulu_broadcast()` → ZULU broadcast to all devices (QTimer at 3600000 ms)
- ZULU sync triggered in GUI (not HealthMonitor) — HealthMonitor only does PING/PONG

### ZULU Time Sync Protocol  
- **Format:** `ZULU:yyyymmdd:hhmmss.xxx` (UTC)
- Sent by `UDPClientThread.send_zulu_sync()` — unicast (default) or broadcast
- Edge device intercepts ZULU at UDP level before all other processing; **does NOT respond**
- Edge calculates: `zulu_offset_ms = ZULU_ms - uptime_ms`; uses offset to timestamp events
- GUI triggers ZULU sync: on first contact, post-FATAL recovery, and hourly broadcast

### Test Edge Device (test_edge_device.py)
Standalone UDP simulator — run with `python test_edge_device.py [--host 0.0.0.0] [--port 5000]`.

Message priority on edge (in order):
1. ZULU sync → parse and store offset, no response
2. PING / PING:timestamp → respond PONG / PONG:timestamp
3. Regular commands (LED, MOTOR, STATUS, ECHO — colon-separated for test device only)

Metrics collection: uses `psutil` (real data) with random fallback if unavailable.
- Temperature: reads `/sys/class/thermal/thermal_zone0/temp` on Linux (Pi), simulates on Windows
- Reports: uptime, temperature, cpu%, memory%

### capstanDrive_worker.py — Command Dictionary Path Note
`capstanDrive_worker.py` loads the command dictionary from:
```
../../../../../shared_dictionaries/command_dictionaries/capstanDrive_commandDictionary.json
```
(5 levels up from its own directory). This is the **shared** dict for the real system. The working development copy is at `core/workers/capstanDrive/capstanDrive_commandDictionary.json`. When testing make sure the shared path resolves, or the worker will run without a command dictionary.

### Metrics Supported
uptime, temperature, cpu, memory (and custom per-device metrics via `health_metrics` key in `servers.json`).

---

## Commands In Menu But Not Yet In Dictionary

The command menu docs and architecture reference these commands that are **not yet defined** in `capstanDrive_commandDictionary.json`:
- `SET_TIME` — System Administration category
- `GET_TIME_STATUS` — System Administration category

These will need to be added to the JSON when implemented.

---

## Adding a New Device Type — Checklist

1. Create `core/workers/newDevice/` with: `__init__.py`, `_worker.py`, `_handler.py`, `_config.py`, `_commandDictionary.json`
2. Define command dictionary with `categories` array + `commands` object
3. Add entry to `data/servers.json` with correct `clientName` matching worker folder name
4. Implement handler functions for each command
5. Restart app — device appears automatically; no code changes elsewhere needed

---

## Status Panel API (key methods)

```python
status_panel.update_table({'key': 'value', ...})   # Table mode
status_panel.set_text('message')                    # Split mode text
status_panel.append_text('message')
status_panel.set_image('path/to/image.png')
status_panel.set_video('path/to/video.mp4')
status_panel.set_video('http://url/stream', is_stream=True)
status_panel.play_video() / pause_video() / stop_video()
```

---

## Roadmap

- **v2.1 (Q2 2026):** Pi 4B integration — H.264 live streaming, RTSP server on Pi, multi-camera, resizable panels, command history.
- **v3.0+:** Web-based remote access, mobile, analytics, ML anomaly detection.
- **Pi 4B networking model:**
  - Commands via **UDP** (same worker/handler/command dictionary pattern as Pico2W devices)
  - Large file transfer (images, videos) via **TCP/IP** — separate channel from commands
  - `StatusPanel` split view (text left, media right) was built specifically for Pi 4B image/video display
- **Pi 4B video dependencies (future):** `picamera2`, `ffmpeg`, `gstreamer` on Pi; `opencv-python`, `aiortc` optional on PC.

---

## Coding Conventions (from Contributing Guide)

- Python 3.8+, PEP8 style
- Keep device logic isolated in its own subfolder
- Use robust error handling and logging
- Update README and relevant docs for any user-facing or architectural changes

---

## Open Items

_(none)_
