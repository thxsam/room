import configparser
from pathlib import Path
import json
from models import Room


CONFIG_FILE = str(Path.home() / ".room" / "config.ini")
ROOM_CONFIG_FILE = str(Path.home() / ".room" / "rooms.json")


def read_config() -> dict:
    """
    Reads the configuration file and returns the default booking settings.

    Returns:
        A dictionary containing the default settings for booking.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return {
        "duration": config.getint(
            "DEFAULT", "duration", fallback=30
        ),  # Default duration in minutes
        "floor": config.getint("DEFAULT", "floor", fallback=3),
        "min_capacity": config.getint("DEFAULT", "min_capacity", fallback=1),
        "email": config.get(
            "DEFAULT", "email", fallback="your.email@descartesunderwriting.com"
        ),
    }


def print_current_config(defaults: dict) -> None:
    """
    Prints the current booking configuration.

    Parameters:
        defaults (dict): A dictionary containing the default settings for booking.
    """
    print("-----------------------------")
    print("Current Booking Configuration:")
    print(f"  Duration (minutes): {defaults['duration']}")
    print(f"  Floor: {defaults['floor']}")
    print(f"  Minimum Capacity: {defaults['min_capacity']}")
    print(f"  email: {defaults['email']}")
    print("-----------------------------")


def load_room_config() -> list[Room]:
    """
    Loads the room configuration from a JSON file.

    Returns:
        A list of Room objects based on the loaded room data.
    """
    with open(ROOM_CONFIG_FILE, "r") as config_file:
        rooms_data = json.load(config_file)
    return [Room(**room) for room in rooms_data]
