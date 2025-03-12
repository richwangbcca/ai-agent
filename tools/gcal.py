import datetime
import re
import os 
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Calendar API setup
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "tools/.gcal_api.json"  # Make sure this is the correct path
class GoogleCalendar:
    def __init__(self):
        """Initialize the Google Calendar service."""
        self.service = self.get_calendar_service()

    def get_calendar_service(self):
        """Authenticates with Google Calendar API and returns the service object."""
        creds = None

        # Load existing credentials
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # If no valid credentials, initiate OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def parse_natural_language_date(self, date_str):
        """Convert natural language dates (e.g., 'March 5th') into 'March 05, 2025' format."""
        # Remove ordinal suffixes (st, nd, rd, th)
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

        # Ensure the day is two digits
        date_parts = date_str.split()
        if len(date_parts) == 2:  # Expected format: ["Month", "Day"]
            month, day = date_parts
            day = day.zfill(2)  # Add leading zero if needed
            current_year = datetime.datetime.now().year  # Get current year
            date_str = f"{month} {day}, {current_year}"  # Add year

        return date_str


    def create_event(self, event_details):
        """
        Creates an event in Google Calendar and returns the event link.
        """
        try:
            # Step 1: Format the date correctly
            date_str = self.parse_natural_language_date(event_details["date"])  # Ensure year is included
            time_str = event_details["time"] if event_details["time"] != "none" else "12:00 PM"

            # Step 2: Normalize time format to ensure it follows "%I:%M %p"
            # If time is "6 PM" or "6PM", convert it to "6:00 PM"
            time_str = re.sub(r"^(\d{1,2})\s?(AM|PM)$", r"\1:00 \2", time_str, flags=re.IGNORECASE)
            time_str = re.sub(r"^(\d{1,2})(AM|PM)$", r"\1:00 \2", time_str, flags=re.IGNORECASE)

            # Remove any extra spaces before ":" (prevents "6 :00 PM" issue)
            time_str = re.sub(r"\s+:", ":", time_str)

            # Ensure proper formatting (removing accidental double spaces)
            time_str = " ".join(time_str.split())

            # Step 3: Remove any unnecessary commas from the date string
            date_str = date_str.replace(",", "").strip()  # Ensure format matches parsing

            # Step 4: Ensure proper format for datetime parsing
            formatted_datetime_str = f"{date_str} {time_str.upper()}"  # Ensure AM/PM is uppercase
            start_datetime = datetime.datetime.strptime(formatted_datetime_str, "%B %d %Y %I:%M %p")

            # Step 5: Set event duration (default 2 hours)
            end_datetime = start_datetime + datetime.timedelta(hours=2)

            # Step 6: Create Google Calendar Event
            event = {
                "summary": event_details["title"],
                "location": event_details["location"] if event_details["location"] != "none" else "TBD",
                "description": f"Theme: {event_details['theme']}" if event_details["theme"] != "none" else "No theme specified",
                "start": {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": "America/Los_Angeles",
                },
                "end": {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "America/Los_Angeles",
                },
                "visibility": "public"
            }

            created_event = self.service.events().insert(calendarId="primary", body=event).execute()
            print(created_event["htmlLink"])
            return created_event["htmlLink"]

        except Exception as e:
            return f"⚠️ Error creating Google Calendar event: {str(e)}"