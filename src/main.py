import sys
from datetime import datetime, timedelta
import pytz
from utils import list_available_rooms, print_rooms_info, create_event, filter_rooms
from authentification import get_credentials
import argparse
from config import read_config, print_current_config, load_room_config
from google.oauth2.credentials import Credentials


def parse_args(defaults: dict) -> argparse.Namespace:
    """
    Parses the command-line arguments.

    Parameters:
    - defaults: A dictionary containing default configuration values.

    Returns:
    - A namespace with the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="List or book available rooms.")
    parser.add_argument("-n", "--name", type=str, help="Name of the room to book.")
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        help="Duration in minutes.",
        default=defaults["duration"],
    )
    parser.add_argument(
        "-f",
        "--floor",
        type=str,
        help="Floor number or 'all' to list all floors.",
        default=defaults["floor"],
    )
    parser.add_argument(
        "-c",
        "--capacity",
        type=int,
        help="Minimum capacity.",
        default=defaults["min_capacity"],
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List available rooms without booking.",
    )
    return parser.parse_args()


def main() -> None:
    """
    The main function to list or book rooms based on command-line arguments.
    """
    default_configuration = read_config()
    rooms = load_room_config()
    print_current_config(default_configuration)

    args = parse_args(default_configuration)
    creds: Credentials = get_credentials()
    start_time: datetime = datetime.now(tz=pytz.UTC)
    end_time: datetime = start_time + timedelta(minutes=args.duration)

    floor: int | None = None if str(args.floor).lower() == "all" else int(args.floor)

    # Load available rooms based on provided filters
    available_rooms = list_available_rooms(creds, start_time, end_time, rooms)

    if args.list:
        filtered_rooms = filter_rooms(
            available_rooms, floor=floor, min_capacity=args.capacity
        )
        print_rooms_info(filtered_rooms, creds, start_time)
        return

    # Booking process
    if args.name:
        normalized_input_name = args.name.strip().lower()
        room_to_book = next(
            (
                room
                for room in available_rooms
                if room.name.strip().lower() == normalized_input_name
            ),
            None,
        )
        if room_to_book:
            create_event(
                creds, room_to_book, args.duration, default_configuration["email"]
            )
        else:
            print(f"Room named '{args.name}' is not available.")
    else:
        # Fallback to booking the first available room if no name is specified
        if available_rooms:
            create_event(
                creds, available_rooms[0], args.duration, default_configuration["email"]
            )
        else:
            print("No available rooms found for booking.")
            sys.exit(1)


if __name__ == "__main__":
    main()
