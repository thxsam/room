from googleapiclient.discovery import build

from datetime import datetime, timedelta
from collections import defaultdict


def list_available_rooms(
    creds, start_time, end_time, rooms, floor: int = None, min_capacity: int = None
):
    service = build("calendar", "v3", credentials=creds)
    body = {
        "timeMin": start_time.isoformat(),
        "timeMax": end_time.isoformat(),
        "items": [{"id": room.id} for room in rooms],
        "timeZone": "UTC",
    }

    response = service.freebusy().query(body=body).execute()

    available_rooms = [
        room
        for room in rooms
        if room.id in response["calendars"]
        and not response["calendars"][room.id]["busy"]
    ]
    if floor is not None:
        available_rooms = [room for room in available_rooms if room.floor == floor]
    if min_capacity is not None:
        available_rooms = [
            room for room in available_rooms if room.capacity >= min_capacity
        ]

    available_rooms_sorted = sorted(
        available_rooms, key=lambda x: (x.floor, x.capacity)
    )
    return available_rooms_sorted


def get_time_until_next_event(service, room_id, start_time):
    # Query the calendar for the next event after 'start_time'
    events_result = (
        service.events()
        .list(
            calendarId=room_id,
            timeMin=start_time.isoformat(),
            maxResults=1,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        return "No upcoming events"

    # Calculate the time difference between 'start_time' and the start of the next event
    next_event_start = datetime.fromisoformat(events[0]["start"]["dateTime"])
    delta = next_event_start - start_time

    # Convert delta to minutes or hours as appropriate
    if delta.total_seconds() < 3600:
        return f"{int(delta.total_seconds() / 60)} minutes"
    else:
        return f"{delta.total_seconds() / 3600:.1f} hours"


def print_rooms_info(available_rooms, creds, start_time):
    if not available_rooms:
        print("No available rooms found.")
        return

    service = build("calendar", "v3", credentials=creds)

    # Group rooms by floor
    rooms_by_floor = defaultdict(list)
    for room in available_rooms:
        rooms_by_floor[room.floor].append(room)

    # Sort the floors before printing
    sorted_floors = sorted(rooms_by_floor.keys())

    print("Available rooms:")
    for floor in sorted_floors:
        print(f"\nFloor {floor}")
        for room in rooms_by_floor[floor]:
            time_until_next_event = get_time_until_next_event(
                service, room.id, start_time
            )
            print(
                f"- Room: {room.name}, Capacity: {room.capacity}, Time until next event: {time_until_next_event}"
            )
    print("-----------------------------")


def create_event(creds, room, duration, email):
    service = build("calendar", "v3", credentials=creds)
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration)

    event = {
        "summary": "Meeting in Room: " + room.name,
        "description": "Automatically scheduled meeting.",
        "start": {"dateTime": start_time.isoformat() + "Z", "timeZone": "UTC"},
        "end": {"dateTime": end_time.isoformat() + "Z", "timeZone": "UTC"},
        "attendees": [{"email": room.id}, {"email": email}],
        "conferenceData": {
            "createRequest": {
                "requestId": "sample123",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    event_result = (
        service.events()
        .insert(calendarId=email, body=event, conferenceDataVersion=1)
        .execute()
    )
    meet_link = event_result.get("hangoutLink")
    print(f"Event created: {event_result.get('htmlLink')}")
    print(f"Meet link: {meet_link}")
    print("-----------------------------")
    print(f"Room booked: {room.name} on floor {room.floor}")
