"""Constants for Kamstrup 403 Kitsok Fork."""

from typing import Final

# Base component constants
NAME: Final = "Kamstrup 403 Kitsok Fork"
DOMAIN: Final = "kamstrup_403"
MODEL: Final = "403"
MANUFACTURER: Final = "Kamstrup"

# Defaults
# Keep sensor name prefix stable for backward-compatible entity IDs.
DEFAULT_NAME: Final = "Kamstrup 403"
DEFAULT_BAUDRATE: Final = 1200
DEFAULT_SCAN_INTERVAL: Final = 3600
DEFAULT_TIMEOUT: Final = 1.0
CONF_DEBUG: Final = "debug"
CONF_BAUDRATE: Final = "baudrate"
CONF_SERIAL_COMMUNICATION_LOGGING: Final = "serial_communication_logging"
