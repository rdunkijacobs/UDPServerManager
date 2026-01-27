# UDP Server Manager

A modular, PySide6-based Supervisor application for managing multiple UDP-connected devices, each with its own worker, command dictionary, and handler logic.

## Features
- Robust UDP networking: single-socket send/receive for reliable device communication
- PySide6 GUI with persistent user preferences
- Per-device worker threads for UDP communication
- Device-specific command dictionaries (JSON)
- Robust error handling and logging
- Scalable, maintainable code structure

## Directory Structure
```
main.py
requirements.txt
app/
    ui/
core/
    udp.py
    workers/
        capstanDrive/
            capstanDrive_worker.py
            capstanDrive_handler.py
            capstanDrive_commandDictionary.json
            capstanDrive_config.py
        ...
docs/
    project_plan.md
    architecture.md
    usage.md
    contributing.md
    message_creator_panel.md
README.md
```

## Getting Started
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the application:
   ```
   python main.py
   ```

## UDP Networking Notes
- The Supervisor uses a single UDP socket per device for both sending and receiving messages. This ensures that all outgoing messages use the same local port as the receive thread, so device responses are always received.
- If you see sent messages but no responses, check that the device is replying to the correct source port (the port shown in the log as 'Sent: ... (from local port ...)').
- For more, see `docs/usage.md` and `docs/architecture.md`.

## Adding a New Device
- Create a new subfolder in `core/workers/` for your device.
- Add a worker, handler, config, and command dictionary as in `capstanDrive/`.
- Register the device in your server configuration.

## Documentation
- See `docs/architecture.md` for design details.
- See `docs/usage.md` for user instructions.
- See `docs/contributing.md` for development guidelines.
- See `docs/message_creator_panel.md` for details on the dynamic message generator, parameter handling, and UI logic. The panel adapts to the command dictionary for each device, supporting dropdowns for enums/booleans and type-in fields for integer/float parameters.

## License
MIT License

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

See `docs/markdown_features_demo.md` for examples.

---
