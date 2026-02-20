# CapstanDrive device configuration

DEVICE_NAME = "CapstanDrive"
DEFAULT_PORT = 5005

# Instance mapping: index to instance name
INSTANCE_MAP = [
	{"index": 0, "name": "MainDrive"},
	{"index": 1, "name": "AuxDrive"}
]

# Mode mapping: index to mode name
MODE_MAP = [
	{"index": 0, "name": "Normal"},
	{"index": 1, "name": "Test"},
	{"index": 2, "name": "Maintenance"}
]

# Boolean encoding configuration
# This defines how boolean values are displayed, encoded, and parsed
# - true_strings: List of values (case-insensitive) that are considered true when parsing
# - false_strings: List of values (case-insensitive) that are considered false when parsing
# - display_options: List of (true_option, false_option) tuples - Available display pairs
#   The command dictionary will specify which tuple to use via the parameter's "options" field
# - message_encoding: [true_value, false_value] - What values to send in messages
# Note: If the device has on()/off() methods, false should always map to off()
BOOLEAN_CONFIG = {
	"true_strings": ["true", "on", "yes", "1"],  # Values considered true
	"false_strings": ["false", "off", "no", "0"],  # Values considered false
	"display_options": [("on", "off"), ("true", "false"), ("yes", "no")],  # Available display pairs
	"message_encoding": ["1", "0"]  # What to send in messages [true_value, false_value]
}

# Command instance counts for populating instance selector
COMMAND_COUNTS= [
	{"command": "LED", "instances": ["redLED","greenLED","blueLED"]},
	{"command": "HPL", "instances": ["actuator"]},
	{"command": "DVR8833", "instances": ["motor"]},
	{"command": "GET_LED", "instances": ["redLED","greenLED","blueLED"]},
	{"command": "GET_HPL", "instances": ["actuator"]},
	{"command": "GET_DVR8833",  "instances": ["motor"]},
	# Add more as needed
]

# Other helpful configuration entries
TIMEOUT_SECONDS = 2.0
RETRY_COUNT = 3
