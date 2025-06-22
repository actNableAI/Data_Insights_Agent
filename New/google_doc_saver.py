from __future__ import print_function
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google Docs + Drive
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file']

def authenticate_google_docs():
    """Authenticate and return the Google Docs service object."""
    creds = None
    token_path = 'auth/token.pickle'
    credentials_path = 'auth/credentials.json'

    # Load existing token
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # Authenticate if no token or expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('docs', 'v1', credentials=creds)

def create_insight_doc(question_id, question_text, insights):
    """Create a new Google Doc with insights and return the Doc URL."""
    service = authenticate_google_docs()

    doc_title = f"Insights Report - {question_id}"
    body = {
        'title': doc_title
    }

    doc = service.documents().create(body=body).execute()
    doc_id = doc['documentId']

    # Content to write
    requests = [
        {'insertText': {'location': {'index': 1}, 'text': f"📊 Insights for {question_id}\n\n"}},
        {'insertText': {'location': {'index': 1}, 'text': f"{question_text.strip()}\n\n"}},
        {'insertText': {'location': {'index': 1}, 'text': f"{insights.strip()}\n"}}
    ]

    service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"
