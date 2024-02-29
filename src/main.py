import sys
from datetime import datetime, timedelta
import pytz
from utils import (
    list_available_rooms,
    print_rooms_info,
    create_event,
)
from authentification import get_credentials
import argparse
from config import read_config, print_current_config, load_room_config


def parse_args(defaults):
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


def main():
    default_configuration = read_config()
    rooms = load_room_config()
    print_current_config(default_configuration)

    args = parse_args(default_configuration)
    creds = get_credentials()
    start_time = datetime.now(tz=pytz.UTC)
    end_time = start_time + timedelta(minutes=args.duration)

    if str(args.floor).lower() == "all":
        args.floor = None
    else:
        args.floor = int(args.floor)

    # Load available rooms based on provided filters
    available_rooms = list_available_rooms(
        creds, start_time, end_time, rooms, floor=args.floor, min_capacity=args.capacity
    )

    if args.list:
        print_rooms_info(available_rooms, creds, start_time)
        return  # Exit after listing available rooms

    # Booking process
    if args.name:
        # Attempt to find and book the specified room
        room_to_book = next(
            (room for room in available_rooms if room.name == args.name), None
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
