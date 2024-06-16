# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# def get_gmail_service():
#     creds = None
#     # Load credentials from token.pickle if it exists
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)

#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             # Specify the port you want to use; this should match the one in the Google Cloud Console
#             creds = flow.run_local_server(port=8080) # Example using port 8080
#         # Save the credentials for the next run
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)

#     service = build('gmail', 'v1', credentials=creds)
#     return service


# service = get_gmail_service()

# # Call the Gmail API to fetch the latest email from INBOX
# results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=1).execute()
# messages = results.get('messages', [])

# if not messages:
#     print("No messages found.")
# else:
#     for message in messages:
#         # Fetch the full message details using the message id
#         msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        
#         # Get the message subject and snippet
#         headers = msg['payload']['headers']
#         subject = next(header['value'] for header in headers if header['name'] == 'Subject')
#         snippet = msg.get('snippet')
        
#         print(f"Latest Email Subject: {subject}")
#         print(f"Snippet: {snippet}")


import os
import pickle
import asyncio
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

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

    service = build('gmail', 'v1', credentials=creds, developerKey='tned swaz tagn ctbu')
    return service

# async def send_email(service):
#     message = """
#     From: Christopher <ctavolazzi@gmail.com>
#     To: Christopher <ctavolazzi@gmail.com>
#     Subject: Test Email

#     This is a test email sent from the Gmail API.
#     """

#     try:
#         message_bytes = message.encode('utf-8')
#         message_base64 = base64.urlsafe_b64encode(message_bytes).decode('utf-8')
#         message = service.users().messages().send(userId='me', body={'raw': message_base64}).execute()
#         print(f'Sent message to ctavolazzi@gmail.com Message Id: {message["id"]}')
#     except Exception as error:
#         print(f'An error occurred: {error}')

# from email.mime.text import MIMEText

# async def send_email(service):
#     message = MIMEText("This is a test email sent from the Gmail API.")
#     message['to'] = "ctavolazzi@gmail.com"
#     message['from'] = "ctavolazzi@gmail.com"
#     message['subject'] = "Test Email AUTHENTICATED!"

#     try:
#         create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
#         send_message = service.users().messages().send(userId="me", body=create_message).execute()
#         print(f'Sent message to ctavolazzi@gmail.com Message Id: {send_message["id"]}')
#     except Exception as error:
#         print(f'An error occurred: {error}')

# async def print_latest_email(service):
#     while True:
#         results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=1).execute()
#         messages = results.get('messages', [])

#         if messages:
#             msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()

#             headers = msg['payload']['headers']
#             subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
#             snippet = msg.get('snippet')

#             print(f"Latest Email Subject: {subject}")
#             print(f"Snippet: {snippet}")

#         await asyncio.sleep(5)

# async def main():
#     service = get_gmail_service()

#     send_email_task = asyncio.create_task(send_email(service))
#     print_email_task = asyncio.create_task(print_latest_email(service))

#     await asyncio.gather(send_email_task, print_email_task)

# asyncio.run(main())


# import os
# import pickle
# import asyncio
# import base64
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from oauth2client import client, tools
# from oauth2client.file import Storage
# from email.mime.text import MIMEText  # Added import statement

# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

# def get_gmail_service():
#     creds = None
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=8080)
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)

#     service = build('gmail', 'v1', credentials=creds)
#     return service

# async def send_email(service):
#     message = MIMEText("This is a test email sent from the Gmail API.")
#     message['to'] = "ctavolazzi@gmail.com"
#     message['from'] = "ctavolazzi@gmail.com"
#     message['subject'] = "Test Email"

#     try:
#         create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
#         send_message = service.users().messages().send(userId="me", body=create_message).execute()
#         print(f'Sent message to ctavolazzi@gmail.com Message Id: {send_message["id"]}')
#     except Exception as error:
#         print(f'An error occurred: {error}')

# async def print_latest_email(service):
#     while True:
#         results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=1).execute()
#         messages = results.get('messages', [])

#         if messages:
#             msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()

#             headers = msg['payload']['headers']
#             subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'Boobies')
#             snippet = msg.get('snippet')

#             print(f"Latest Email Subject: {subject}")
#             print(f"Snippet: {snippet}")

#         await asyncio.sleep(5)

# async def main():
#     service = get_gmail_service()

#     send_email_task = asyncio.create_task(send_email(service))
#     print_email_task = asyncio.create_task(print_latest_email(service))

#     await asyncio.gather(send_email_task, print_email_task)

# asyncio.run(main())



import os
import pickle
import asyncio
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

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

async def send_email(service):
    message = MIMEText("This is a test email sent from the Gmail API.")
    message['to'] = "aziah97@gmail.com"
    message['subject'] = "Test Email"

    try:
        message_encoded = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        create_message = {'raw': message_encoded}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f'Sent message to ctavolazzi@gmail.com Message Id: {send_message["id"]}')
    except Exception as error:
        print(f'An error occurred: {error}')

async def main():
    service = get_gmail_service()
    await send_email(service)

asyncio.run(main())