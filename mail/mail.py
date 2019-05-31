import base64
import json
import re
import templates

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

    if reply_to != {}:
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

    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()

    raw_message = {'raw': b64_string}

    return raw_message


def main():
    creds = get_credentials()
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    for msg in get_mail(service):
        threadId = msg['threadId']

        header_dict = {header['name']:header['value'] for header in msg['payload']['headers']}
        
        reply_dict = {'threadId': threadId}
        reply_dict.update(header_dict)

        first_name, last_name, addr = re.search(r'(?:(\w+)\s+(\w+))\s+<(\w+@\w+\.\w+)>', header_dict['From']).groups()

        new_msg = create_mail(addr, header_dict['Subject'], templates.REPLY.format(first_name), reply_dict)
        service.users().messages().send(userId = 'me', body = new_msg).execute()
    

if __name__ == '__main__':
    main()

