# Command Dictionaries – Tutorial & Reference

---

## Purpose
Command dictionaries define the set of commands and messages that the Supervisor (UDPServerManager) and SpoolerController use to communicate with edge servers. They ensure that both sides understand the meaning and format of every command sent or received.

---

## What is a Command Dictionary?
A command dictionary is a list of all possible commands, their parameters, and their expected responses. In embedded C, this is similar to an enum or a set of #define constants for command IDs, plus a struct for command data.

---

## Typical Contents
- **Command name** (e.g., START, STOP, SET_SPEED)
- **Command ID** (numeric or string identifier)
- **Parameters** (what data is needed)
- **Expected response** (acknowledgment, data, error)

---

## Example (Python-style, but easy to read)
```python
COMMANDS = {
    "START": {"id": 1, "params": []},
    "STOP": {"id": 2, "params": []},
    "SET_SPEED": {"id": 3, "params": ["speed"]},
    "GET_STATUS": {"id": 4, "params": []}
}
```

---

## How Embedded C Users Can Relate
- Think of the command dictionary as a set of #define or enum values for command IDs, and a struct for each command's data.
- Instead of hard-coding command values in multiple places, you keep them in one place for consistency.
- Both Python and C code can use the same command IDs and parameter lists (documented here).

---

## Example Table (Markdown)
| Command Name | ID  | Parameters   | Response         |
|--------------|-----|--------------|------------------|
| START        | 1   | (none)       | ACK/ERROR        |
| STOP         | 2   | (none)       | ACK/ERROR        |
| SET_SPEED    | 3   | speed (int)  | ACK/ERROR        |
| GET_STATUS   | 4   | (none)       | status (struct)  |

---

## Editing and Extending
- Add new commands by updating the dictionary and this documentation.
- Make sure both Python and embedded C code use the same IDs and parameter names.
- Document any changes for future maintainers.

---

## Best Practices
- Keep command IDs unique and consistent.
- Use clear, descriptive names for commands and parameters.
- Document expected responses for each command.

---

## Summary
- Command dictionaries are the shared language between Supervisor, SpoolerController, and edge servers.
- They are easy to update and understand, even for non-Python users.
- Treat them like enums and structs in embedded C: update as new features are added, and keep documentation in sync.

---

## Dynamic UI Integration
- The message creator panel reads the command dictionary and adapts the UI for each command and parameter.
- Enum/boolean parameters are shown as dropdowns; integer/float as type-in fields.
- Mode parameters are sent as their dropdown index (1-based), not as text.
- Boolean values are always sent as '1' (true/on) or '0' (false/off).
- Only parameters relevant to the selected mode are shown and included in the message.

---

## Adding/Editing Device Classes
- To add a new device class, create a new command dictionary JSON and config file in `core/workers/<device>/`.
- Follow the structure and best practices in this document and `message_creator_panel.md`.
- Test new classes in the UI to ensure correct parameter mapping and message assembly.
