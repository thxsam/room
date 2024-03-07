from googleapiclient.discovery import build
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
from google.oauth2.credentials import Credentials
from models import Room


def create_event(creds: Credentials, room: Room, duration: int, email: str) -> None:
    """
    Creates an event in the Google Calendar for the specified room.

    Parameters:
    - creds: Credentials object for Google API authentication.
    - room: The room object for which to create the event.
    - duration: Duration of the event in minutes.
    - email: Email address to be added as an attendee to the event.

    """
    service = build("calendar", "v3", credentials=creds)
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration)

    event_body = {
        "summary": f"Meeting in Room: {room.name}",
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
        .insert(calendarId=email, body=event_body, conferenceDataVersion=1)
        .execute()
    )
    meet_link = event_result.get("hangoutLink")
    print(f"Event created: {event_result.get('htmlLink')}")
    print(f"Meet link: {meet_link}")
    print("-----------------------------")
    print(f"Room booked: {room.name} on floor {room.floor}")


def list_available_rooms(
    creds: Credentials,
    start_time: datetime,
    end_time: datetime,
    rooms: list,
    chunk_size: int = 10,
) -> list:
    """
    Lists available rooms based on their free/busy status in Google Calendar.

    Parameters:
    - creds: Credentials object for Google API authentication.
    - start_time: The start datetime to check room availability.
    - end_time: The end datetime to check room availability.
    - rooms: A list of room objects to check availability for.
    - chunk_size: The number of rooms to query for availability in each batch.

    Returns:
    - A sorted list of available rooms based on floor and capacity.
    """
    service = build("calendar", "v3", credentials=creds)
    available_rooms = []
    for i in range(0, len(rooms), chunk_size):
        chunked_rooms = rooms[i : i + chunk_size]
        body = {
            "timeMin": start_time.isoformat(),
            "timeMax": end_time.isoformat(),
            "items": [{"id": room.id} for room in chunked_rooms],
            "timeZone": "UTC",
        }

        response = service.freebusy().query(body=body).execute()

        for room in chunked_rooms:
            if room.id in response["calendars"] and not response["calendars"][
                room.id
            ].get("busy"):
                available_rooms.append(room)

    available_rooms_sorted = sorted(
        available_rooms, key=lambda x: (x.floor, x.capacity)
    )
    return available_rooms_sorted


def get_time_until_next_event(
    service,
    room_id: str,
    start_time: datetime,
) -> str:
    """
    Calculates the time until the next event for a given room.

    Parameters:
    - service: The Google Calendar API service instance.
    - room_id: The ID of the room to check.
    - start_time: The datetime from which to start checking for the next event.

    Returns:
    - A string indicating the time until the next event.
    """
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

    next_event_start = datetime.fromisoformat(events[0]["start"]["dateTime"])
    delta = next_event_start - start_time
    if delta.total_seconds() < 3600:
        return f"{int(delta.total_seconds() / 60)} minutes"
    else:
        return f"{delta.total_seconds() / 3600:.1f} hours"


def print_rooms_info(
    available_rooms: list,
    creds: Credentials,
    start_time: datetime,
) -> None:
    """
    Prints information about available rooms.

    Parameters:
    - available_rooms: A list of available room objects.
    - creds: Credentials object for Google API authentication.
    - start_time: The datetime for which room availability was checked.
    """
    if not available_rooms:
        print("No available rooms found.")
        return

    service = build("calendar", "v3", credentials=creds)
    rooms_by_floor = defaultdict(list)
    for room in available_rooms:
        rooms_by_floor[room.floor].append(room)

    print("Available rooms:")
    for floor in sorted(rooms_by_floor.keys()):
        print(f"\nFloor {floor}")
        for room in rooms_by_floor[floor]:
            time_until_next_event = get_time_until_next_event(
                service, room.id, start_time
            )
            print(
                f"- Room: {room.name}, Capacity: {room.capacity}, Time until next event: {time_until_next_event}"
            )
    print("-----------------------------")


def filter_rooms(
    rooms: list,
    floor: Optional[int] = None,
    min_capacity: Optional[int] = None,
) -> list:
    """
    Filters a list of rooms by floor and minimum capacity.

    Parameters:
    - rooms: A list of room objects.
    - floor: Optional; the specific floor to filter the rooms by.
    - min_capacity: Optional; the minimum capacity required for the rooms.

    Returns:
    - A list of room objects that meet the specified criteria.
    """
    if floor is not None:
        rooms = [room for room in rooms if room.floor == floor]
    if min_capacity is not None:
        rooms = [room for room in rooms if room.capacity >= min_capacity]
    return rooms
