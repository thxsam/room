# Room Booking Utility

This utility is designed to facilitate the booking of rooms through Google Calendar, offering a command-line interface for listing available rooms and booking them automatically. It integrates with the Google Calendar API to check room availability, create events, and include Google Meet links for virtual meetings.

## Features

- **List Available Rooms**: View all available rooms for a specified duration, floor, and capacity.
- **Quick Booking**: Directly book an available room matching your default configuration
- **Book a Room by Name**: Directly book an available room by specifying its name.
- **Configuration File Support**: Customize default settings such as booking duration, preferred floor, and minimum capacity through a configuration file.
- **Display Time Until Next Meeting**: For each available room, see how long it is until the next scheduled meeting.

## Setup

1. **Clone the Repository**: Start by cloning this repository to your local machine.

   ```bash
   git clone https://repository-url.git
   cd room
   ```
2. **Install Dependencies**: Ensure you have Python 3.7+ installed, then set up a virtual environment and install the required packages.

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
3. **Google Calendar API**: Follow the [Google Calendar API Quickstart](https://developers.google.com/calendar/quickstart/python) to set up your credentials. Save the credentials file as `credentials.json` in `~/.room/credentials.json`
4. **Configuration**: Create the `~/.room/config.ini` file in your home directory and set your default values and email.

   ```ini
   [DEFAULT]
   duration=30
   floor=3
   min_capacity=1
   email=your.email@example.com
   ```

## Usage

- **List Available Rooms**: Run the utility with the `-l` flag to list all available rooms.

  ```bash
  python main.py -l
  ```
- **Book a Room**: Specify the name of the room you wish to book using the `-n` option.

  ```bash
  ²python main.py -n "Room Name"
  ```
- **Specify Duration, Floor, and Capacity**: Use the `-d`, `-f`, and `-c` options to set the duration (in minutes), floor, and minimum capacity, respectively.

  ```bash
  python main.py -d 60 -f 2 -c 4
  ```

## Customization

Edit the `.room/config.ini` file to change the default settings. These defaults will be used unless overridden by command-line arguments.

## Contributing

Contributions to improve this utility are welcome. Please follow the standard fork-and-pull request workflow.

## License

[MIT License](LICENSE)
