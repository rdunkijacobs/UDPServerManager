# Message Creator Panel – Care & Feeding

## Overview
The Message Creator Panel is a dynamic, modular UI component that allows users to assemble and send device-specific UDP messages. It adapts to the command dictionary for each device, supporting dropdowns for enums/booleans and type-in fields for integer/float parameters.

## How It Works
- The panel reads the command dictionary for the selected device/class.
- For each command, it dynamically creates dropdowns or type-in fields for parameters, based on their type and mode.
- Dropdowns are used for enum/boolean parameters; type-in fields (QLineEdit) are used for integer/float parameters.
- The message string is assembled in real time, using dropdown indices for modes and translating booleans to '1'/'0'.
- Only parameters relevant to the selected mode are shown and included in the message.

## Extending/Modifying
- To add a new device/class, update the command dictionary JSON and config as described in the tutorials.
- To add a new parameter type, ensure the UI logic in `message_creator_panel.py` handles it (dropdown for enums/booleans, type-in for int/float).
- The panel will automatically adapt to new commands and parameter types if the dictionary is updated correctly.

## Best Practices
- Keep command dictionaries up to date and well-documented.
- Use unique, descriptive names for commands and parameters.
- Test new device classes in the UI to ensure correct field rendering and message assembly.

## Troubleshooting
- If a parameter does not appear, check its `condition` and type in the command dictionary.
- If the message is not assembled as expected, verify the parameter mapping and types.

---

See also: `command_dictionary_tutorial.md`, `config_file_tutorial.md`, and `README.md` for more details.
