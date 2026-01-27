# Servers File (servers.json) – Tutorial & Reference

---

## Purpose
The `servers.json` file lists all the devices (servers) that the Supervisor (UDPServerManager) can manage. It organizes devices by location and provides the information needed to connect and communicate with each one.

---

## What is a Servers File?
A servers file is a structured list (in JSON format) that tells the software which devices exist, where they are, and how to reach them. This is similar to a device table or lookup table in embedded C systems.

---

## Typical Contents
- **Location** (e.g., xiTechnology, ANZA, DNS)
- **Device name** (e.g., TransferTapeBrake, SpeedSensor)
- **IP address**
- **Port number**
- **Role or type**

---

## Example (JSON)
```json
{
  "xiTechnology": [
    {"name": "TransferTapeBrake", "ip": "192.168.1.10", "port": 5000, "role": "brake"},
    {"name": "SpeedSensor", "ip": "192.168.1.11", "port": 5001, "role": "sensor"}
  ],
  "ANZA": [
    {"name": "capstanDrive", "ip": "192.168.2.10", "port": 5000, "role": "drive"}
  ]
}
```

---

## How Embedded C Users Can Relate
- Think of `servers.json` as a table in flash or a struct array in C that holds device info.
- Instead of hard-coding device addresses, you keep them in this file for easy updates.
- The Python code reads this file at startup to know which devices to manage.

---

## Editing the Servers File
- Use any text editor (Notepad, VS Code, etc.).
- The format is JSON: curly braces `{}` for objects, square brackets `[]` for lists.
- Each location is a key, and its value is a list of device objects.
- Example addition:
```json
"DNS": [
  {"name": "QA Sensor", "ip": "192.168.3.10", "port": 6000, "role": "sensor"}
]
```

---

## Best Practices
- Keep a backup before making changes.
- Make sure the JSON format is valid (no trailing commas, matching braces).
- Use clear, descriptive names for devices and locations.

---

## Summary
- `servers.json` is the master list of all devices the Supervisor manages.
- It is easy to update and understand, even for non-Python users.
- Treat it like a device table in embedded systems: update as hardware changes, no code changes needed.
