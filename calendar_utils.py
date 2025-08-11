# calendar_utils.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from Main import create_message, send_email, FROM_EMAIL
import pytz

def create_google_meeting(service, summary, description, start_time, duration_minutes, attendee_email):
    try:
        calendar_service = build('calendar', 'v3', credentials=service._http.credentials)

        timezone = 'Asia/Karachi'
        start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end = start + timedelta(minutes=duration_minutes)
        start = start.astimezone(pytz.timezone(timezone))
        end = end.astimezone(pytz.timezone(timezone))

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': timezone,
            },
            'attendees': [{'email': attendee_email}],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet_{datetime.now().timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
        }

        event = calendar_service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1,
            sendUpdates='all'
        ).execute()

        return event.get('hangoutLink', 'No link generated')

    except HttpError as error:
        print(f"❌ Calendar error: {error}")
        return None

def send_meeting_confirmation(service, meet_link, recipient_email):
    subject = "Meeting Confirmation – Google Meet Link"
    body_html = (
        f"<p style='font-family:Arial, sans-serif;'>Dear {recipient_email.split('@')[0]},</p>"
        "<p>Your meeting has been scheduled. You can join using the following Google Meet link:</p>"
        f"<p><a href='{meet_link}'>{meet_link}</a></p>"
        "<br><p style='font-family:Arial, sans-serif;'>Looking forward to speaking with you.</p>"
        "<p style='font-family:Arial, sans-serif;'>Best regards,<br>Jamshaid Basit</p>"
    )
    message = create_message(FROM_EMAIL, recipient_email, subject, body_html)
    send_email(service, "me", message)
