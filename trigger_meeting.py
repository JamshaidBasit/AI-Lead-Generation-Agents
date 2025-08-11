# trigger_meeting.py

from calendar_utils import create_google_meeting, send_meeting_confirmation
from Main import gmail_authenticate, TO_EMAIL

def main():
    print("📅 Meeting Scheduler")

    meeting_time = input("🕒 Enter meeting start time (YYYY-MM-DD HH:MM): ").strip()
    duration = int(input("⏱️ Enter meeting duration in minutes: ").strip() or 30)
    recipient_email = TO_EMAIL

    print("🔐 Authenticating with Gmail/Calendar...")
    gmail_service = gmail_authenticate()

    print("📆 Creating Google Calendar event...")
    meet_link = create_google_meeting(
        service=gmail_service,
        summary="AI Collaboration Meeting",
        description="Follow-up discussion after email confirmation.",
        start_time=meeting_time,
        duration_minutes=duration,
        attendee_email=recipient_email
    )

    if meet_link:
        print(f"✅ Meet link: {meet_link}")
        confirm = input("📤 Send confirmation email to recipient? (yes/no): ").strip().lower()
        if confirm == 'yes':
            send_meeting_confirmation(gmail_service, meet_link, recipient_email)
    else:
        print("❌ Failed to create meeting.")

if __name__ == '__main__':
    main()
