# UDP Server Manager Architecture

## Overview
This project is a modular Supervisor for managing UDP-connected devices. Each device type has its own worker, handler, and command dictionary, allowing for scalable and maintainable code.

## Key Components
- **main.py**: Application entry point, loads server configs, starts GUI.
- **core/udp.py**: Manages UDP networking and worker thread lifecycle. Uses a single UDP socket per device for both sending and receiving, ensuring all responses are received on the correct port.
- **core/workers/**: Contains per-device subfolders with worker, handler, config, and command dictionary files.
- **app/ui/**: (If present) GUI components and resources.

## Worker/Handler Pattern
- Each device type (e.g., capstanDrive) has:
  - A worker thread for UDP communication and mailbox logic
  - A handler for device-specific command logic
  - A JSON command dictionary
  - A config file for device constants

## Communication Flow
1. Supervisor loads server list and starts a worker per device.
2. Each worker (UDPClientThread) creates a single UDP socket, binds to an ephemeral port, and uses it for both sending and receiving.
3. When a message is sent, the log shows the local port used. Devices must reply to this port for responses to be received.
4. Worker receives commands (from GUI or UDP), looks up in its dictionary, and dispatches to handler.
5. Handler executes logic, may send responses or errors via mailbox.
6. Supervisor collects responses for UI or logging.

## Error Handling
- All errors are logged with context.
- UDP port mismatches are a common source of missing responses. Always check the log for the local port and ensure devices reply to it.
- Workers and handlers are robust to malformed commands and network issues.

## Extending the System
- Add a new device by creating a subfolder in `core/workers/` and following the capstanDrive example.
- Update server configuration as needed.

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
See `usage.md` for user instructions and `contributing.md` for development guidelines.
