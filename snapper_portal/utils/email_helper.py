import os
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_credentials():
    """get user credentials"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('snapper_portal/config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_verification_code():
    """get verification code from the email"""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    # get the email list and get the verify code email
    results = service.users().messages().list(userId='me', q="subject:One last step to send your Snap").execute()
    messages = sorted(results.get('messages', []), key=lambda x: x.get('internalDate', 0), reverse=True)
    
    if messages:
        # Get the first one last step email
        message = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
        
        # Get the content in the email
        msg_raw = ""
        if 'payload' in message:
            parts = message['payload'].get('parts', [])
            if not parts:
                # If no parts get the content
                msg_raw = base64.urlsafe_b64decode(message['payload']['body']['data'].encode('UTF-8')).decode('utf-8')
            else:
                # if has parts，check every parts.
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        msg_raw = base64.urlsafe_b64decode(part['body']['data'].encode('UTF-8')).decode('utf-8')
                        break
        
        # get the code
        match = re.search(r'\b\d{4}\b', msg_raw)  # 
        if match:
            print(f"Verification code: {match.group()}")
            return match.group()
        else:
            print("Cannot find the verificaiton code")
    else:
        print("Cannot find the email")

# Get the code
if __name__ == "__main__":
    get_verification_code()