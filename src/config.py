import configparser
from pathlib import Path
import json
from models import Room


CONFIG_FILE = str(Path.home() / ".room" / "config.ini")
ROOM_CONFIG_FILE = str(Path.home() / ".room" / "rooms.json")


def read_config():
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


def print_current_config(defaults):
    print("-----------------------------")
    print("Current Booking Configuration:")
    print(f"  Duration (minutes): {defaults['duration']}")
    print(f"  Floor: {defaults['floor']}")
    print(f"  Minimum Capacity: {defaults['min_capacity']}")
    print(f"  email: {defaults['email']}")
    print("-----------------------------")


def load_room_config() -> list[Room]:
    with open(ROOM_CONFIG_FILE, "r") as config_file:
        rooms_data = json.load(config_file)
    return [Room(**room) for room in rooms_data]
