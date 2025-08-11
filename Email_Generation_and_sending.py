import os
import pickle
import base64
import requests
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --------- Configurations ---------
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"  # Replace with your Groq API key

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
FROM_EMAIL = "jamshaidbasit0011@gmail.com"
TO_EMAIL = "fatimanur146@gmail.com"

# ----------------------------------

def get_groq_email_body(name, title, company):
    prompt = (
        f"Write a highly professional, formal, and polished cold email addressed to {name}, who is {title} at {company}. "
    "The email should be concise yet elegant, emphasizing potential digital marketing collaboration. "
    "DO NOT include any closing phrase, signature, or valediction such as 'Best regards', 'Sincerely', or 'Thank you'. "
    "Only write the main body of the email without any sign-off. "
    "Keep the tone courteous, confident, and business-appropriate." 
    "Do NOT include or guess any email addresses or contact information of the recipient." \
    "Donot add Recipient Name at end of mail"
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {"role": "system", "content": "You are a professional email writing assistant."},
            {"role": "user", "content": prompt}
        ],
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "temperature": 0.0,
        "max_tokens": 350
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()
    generated_text = result["choices"][0]["message"]["content"].strip()
    if not generated_text:
        raise Exception("No email content received from Groq API")
    return generated_text

def gmail_authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, body_html):
    message = MIMEText(body_html, 'html')  # Use 'html' instead of 'plain'
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(service, user_id, message):
    sent_message = service.users().messages().send(userId=user_id, body=message).execute()
    print(f"✅ Email sent successfully! Message ID: {sent_message['id']}")

def main():
    recipient_name = "Fatima Nur"
    recipient_title = "ML/AI Engineer"
    recipient_company = "Bitetech Solution"
    subject = "For AI services"

    print("🧠 Generating email content using Groq API...")
    email_body_text = get_groq_email_body(recipient_name, recipient_title, recipient_company)

    # Convert AI plain text to simple HTML paragraphs
    # Split by lines and wrap each non-empty line in <p>
    lines = [line.strip() for line in email_body_text.split('\n') if line.strip()]
    email_body_html = "".join(f"<p style='font-family:Arial, sans-serif; font-size:14px; line-height:1.2;'>{line}</p>" for line in lines)

    # Your fixed signature in HTML format
    signature_html = (
        "<br><br>"
        "<p style='font-family:Arial, sans-serif; font-size:14px; line-height:1.5;'>Best regards,</p>"
        "<p style='font-family:Arial, sans-serif; font-size:14px; line-height:1.0; font-weight:bold;'>Jamshaid Basit</p>"
        "<p style='font-family:Arial, sans-serif; font-size:14px; line-height:0.8;'>Bitetch Solutions</p>"
    )

    full_email_html = email_body_html + signature_html

    print(f"\n📧 Generated Email HTML:\n{full_email_html}\n")

    print("🔐 Authenticating with Gmail API...")
    gmail_service = gmail_authenticate()

    print(f"📤 Sending email to {TO_EMAIL}...")
    message = create_message(FROM_EMAIL, TO_EMAIL, subject, full_email_html)
    send_email(gmail_service, "me", message)

if __name__ == '__main__':
    main()
