from google_auth_oauthlib.flow import InstalledAppFlow
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from pathlib import Path

CREDENTIALS_PATH = str(Path.home() / ".room" / "credentials.json")
TOKEN_PATH = str(Path.home() / ".room" / "token.json")
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]


def get_credentials() -> Credentials:
    """
    Gets the Google OAuth2 credentials. Attempts to use the saved token,
    refresh it if necessary, or creates a new one if the token is missing or invalid.

    Returns:
        Credentials: The OAuth2 credentials for the Google API.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds
