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
