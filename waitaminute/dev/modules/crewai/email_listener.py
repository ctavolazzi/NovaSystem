import os
import pickle
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def process_email(email):
    subject = email['payload']['headers']
    subject = next((header['value'] for header in subject if header['name'] == 'Subject'), 'No Subject')
    sender = email['payload']['headers']
    sender = next((header['value'] for header in sender if header['name'] == 'From'), 'Unknown Sender')
    body = email['snippet']

    print(f"New email received:")
    print(f"Subject: {subject}")
    print(f"From: {sender}")
    print(f"Body: {body}")

def listen_for_emails():
    service = get_gmail_service()
    print("Listening for new emails...")

    while True:
        try:
            email_event = service.users().messages().list(userId='me', q='is:unread').execute()
            emails = email_event.get('messages', [])

            for email in emails:
                email_data = service.users().messages().get(userId='me', id=email['id']).execute()
                process_email(email_data)
                
                service.users().messages().modify(userId='me', id=email['id'], body={'removeLabelIds': ['UNREAD']}).execute()

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            break

if __name__ == '__main__':
    listen_for_emails()