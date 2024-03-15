import os
import asyncio
import base64
import pickle
import json
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, Process
from crewai_tools import BaseTool
from langchain_community.llms import Ollama  # Ensure this import is correct based on your environment
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging

# Load environment variables
load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Gmail API configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

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

# Assuming instantiation of local_llm is successful
local_llm = Ollama(model=os.getenv('MODEL'))


class FetchLatestEmailTool(BaseTool):
    name: str = "Fetch Latest Email"
    description: str = "Fetches the latest unread email from the inbox."

    async def _run(self) -> dict:
        service = get_gmail_service()
        result = await service.users().messages().list(userId='me', q='is:unread').execute()
        messages = result.get('messages', [])
        if not messages:
            return {"error": "No new unread emails found."}

        message_id = messages[0]['id']
        message = await service.users().messages().get(userId='me', id=message_id).execute()
        payload = message['payload']
        headers = payload['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
        body_data = None
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body_data = part['body']['data']
                    break
        if not body_data:
            body_data = payload['body']['data']
        text = base64.urlsafe_b64decode(body_data).decode('utf-8')
        await service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()

        return {"subject": subject, "sender": sender, "text": text}

class LLMRecommendationTool(BaseTool):
    name: str = "LLM Recommendation"
    description: str = "Analyzes email content and generates recommendations."

    async def _run(self, email_content: dict) -> str:
        # Assuming `local_llm` is a previously instantiated Ollama object with async support
        processed_content = f"Please analyze this email content and suggest actions:\n\n{email_content['text']}"
        recommendation = await local_llm.generate(processed_content, max_tokens=100)  # This is a placeholder
        return recommendation



# Load or refresh credentials
def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.readonly'])
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Fetch the latest unread email
def fetch_latest_unread_email(service):
    try:
        results = service.users().messages().list(userId='me', q='is:unread', maxResults=1).execute()
        messages = results.get('messages', [])
        if not messages:
            print('No unread messages found.')
            return None

        message_id = messages[0]['id']
        msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()

        payload = msg['payload']
        headers = payload.get('headers')
        parts = payload.get('parts')[0]
        data = parts['body']['data']
        body = base64.urlsafe_b64decode(data).decode('utf-8')

        email_details = {
            "id": message_id,
            "snippet": msg.get('snippet', ''),
            "body": body
        }

        for header in headers:
            if header['name'] == 'Subject':
                email_details['subject'] = header['value']
            elif header['name'] == 'From':
                email_details['from'] = header['value']

        return email_details

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

# Simulate processing and making a recommendation
def process_email_and_recommend(email_details):
    # Placeholder for processing logic; in practice, this could involve analyzing the email's content
    # Here we simply make a basic recommendation based on the presence of a keyword
    instructions = "Please analyze this email content and suggest actions in English:\n\n"

    prompt = f"{instructions}{email_details['body']}"

    recommendation = local_llm.invoke(prompt)

    print(f"Recommendation: {recommendation}")
    return recommendation

# Define your agents
email_agent = Agent(
    role="Email Agent",
    goal="Process emails and generate actionable insights.",
    backstory="A sophisticated AI agent capable of understanding and categorizing emails.",
    llm=local_llm,
    # tools=[FetchLatestEmailTool(), LLMRecommendationTool(), SaveEmailAsJSONTool()],
    verbose=True
)

# Define tasks and crew
fetch_email_task = Task(
    description="Fetch the latest unread email.",
    expected_output="Email content as a dictionary.",
    agent=email_agent,
    # tools=[FetchLatestEmailTool()]
)

analyze_email_task = Task(
    description="Analyze email content and generate a recommendation.",
    expected_output="A recommendation string.",
    agent=email_agent,
    # tools=[LLMRecommendationTool()],
    context=[fetch_email_task]
)

save_email_task = Task(
    description="Compile email content and recommendation into a JSON object and save.",
    expected_output="Confirmation of JSON saved.",
    agent=email_agent,
    # tools=[SaveEmailAsJSONTool()],
    context=[analyze_email_task]
)


email_crew = Crew(
    agents=[email_agent],
    tasks=[fetch_email_task, analyze_email_task],
    process=Process.sequential
)

# async def main():
#     await email_crew.kickoff()

# if __name__ == "__main__":
#     asyncio.run(main())

def main():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    email_details = fetch_latest_unread_email(service)
    if email_details:
        print(json.dumps(email_details, indent=2))
        process_email_and_recommend(email_details)

if __name__ == "__main__":
    main()