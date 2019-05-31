import base64

from email.mime.text import MIMEText
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pathlib import Path


ABS_PATH = Path().resolve() / 'mail'
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'


def get_credentials():
    store = file.Storage(ABS_PATH / 'token.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(ABS_PATH / 'client_secrets.json', SCOPES)
        creds = tools.run_flow(flow, store)
        store.put(creds)
    
    return creds


def get_mail(service):
    results = service.users().messages().list(userId='me',labelIds = ['UNREAD']).execute()
    messages = results.get('messages', [])

    if messages:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            service.users().messages().modify(
                userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}
            ).execute()
            yield msg


def create_mail(to: str, subject: str, message_text: str, reply_to: {str: str} = None) -> {}:
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = 'emailchessraff@gmail.com'
    message['subject'] = subject

    if reply_to:
        message['threadId'] = reply_to['threadId']
        message['Message-ID'] = reply_to['Message-ID']
        
        if 'In-Reply-To' in reply_to:
            message['In-Reply-To'] = reply_to['In-Reply-To']
        else:
            message['In-Reply-To'] = reply_to['Message-ID']

        if 'References' in reply_to:
            message['References'] = reply_to['References']
        else:
            message['References'] = reply_to['Message-ID']

    print(message.as_string())

    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()

    raw_message = {'raw': b64_string}

    return raw_message


def main():
    creds = get_credentials()
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    return service
    

if __name__ == '__main__':
    main()

