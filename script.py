import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)
def delete_unwanted_emails():
    print("🚀 Connecting to Gmail...")
    service = authenticate_gmail()

    labels = service.users().labels().list(userId='me').execute()
    label_id = next((l['id'] for l in labels['labels'] if l['name'].lower() == 'unwanted email'), None)

    if not label_id:
        print("❌ Label not found.")
        return

    print("🔍 Retrieving all emails...")
    all_messages = []
    next_page_token = None

    while True:
        response = service.users().messages().list(
            userId='me',
            labelIds=[label_id],
            maxResults=100,
            pageToken=next_page_token
        ).execute()

        all_messages.extend(response.get('messages', []))
        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    print(f"🧹 Deleting {len(all_messages)} emails...")

    for msg in all_messages:
        service.users().messages().trash(userId='me', id=msg['id']).execute()
        print(f"🗑️ Moved to trash: {msg['id']}")

    print("✅ All emails moved to Trash.")


if __name__ == '__main__':
    delete_unwanted_emails()
