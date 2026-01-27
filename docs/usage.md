# Usage Guide: UDP Server Manager

## Running the Application
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Start the Supervisor:
   ```
   python main.py
   ```

## UDP Networking & Troubleshooting
- The Supervisor uses a single UDP socket for both sending and receiving. This means all outgoing messages use the same local port as the receive thread, so device responses are always received.
- If you see 'Sent: ... (from local port ...)' but never see 'Received from ...', your device may be replying to a different port. Ensure the device replies to the source port of the incoming message.
- All errors are logged to the console and/or log file.
- If a device is not responding, check network settings and device status.
- For persistent issues, review the architecture and contributing docs.

## GUI Overview
- The main window lists all configured servers/devices.
- Select a device to view status, send commands, and see responses.
- Preferences (window size, last device, etc.) are saved automatically.

## Adding/Editing Devices
- Edit your server configuration file (e.g., `servers.json`).
- Add a new device by following the structure in `core/workers/`.

## Message Creation

- The message creator panel adapts to the selected device and command.
- Dropdowns are used for enum/boolean parameters; type-in fields for integer/float.
- The message string is assembled in real time, using dropdown indices for modes and translating booleans to '1'/'0'.
- Only parameters relevant to the selected mode are shown and included in the message.

See `docs/message_creator_panel.md` for advanced usage and troubleshooting.

## Troubleshooting
- All errors are logged to the console and/or log file.
- If a device is not responding, check network settings and device status.
- For persistent issues, review the architecture and contributing docs.

## Support
- For help, contact the project maintainer or open an issue in your version control system.

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
