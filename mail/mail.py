import base64
import json
import re

from email.mime.text import MIMEText
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pathlib import Path


SCOPES = 'https://www.googleapis.com/auth/gmail.modify'

REPLY_TEMPLATE = "Hello, {}!\r\n\r\nThank you for sending me mail! 😊\r\nI'm currently in development, so this is all I can reply with. 😔\r\nBut come back later and there will probably be more stuff then!"
SARAH_TEMPLATE = "Hello, {}!\r\n\r\nThank you for sending me mail! 😊\r\nI'm currently in development, so this is all I can reply with. 😔\r\nBut come back later and there will probably be more stuff then!\r\n\r\nBTW, Raff says he loves you. 😍"

def get_credentials():
    abs_path = Path().resolve() / 'mail'

    store = file.Storage(abs_path / 'token.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(abs_path / 'client_secrets.json', SCOPES)
        creds = tools.run_flow(flow, store)
        store.put(creds)
    
    return creds


def get_mail(service):
    results = service.users().messages().list(userId='me',labelIds = ['UNREAD']).execute()
    messages = results.get('messages', [])

    if messages:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}).execute()
            yield msg


def create_mail(to: str, subject: str, message_text: str, reply_to: str = None) -> {}:
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = 'emailchessraff@gmail.com'
    message['subject'] = subject

    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()

    raw_message = {'raw': b64_string}
    
    if reply_to:
        raw_message['threadId'] = reply_to

    return raw_message


def main():
    creds = get_credentials()
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    for msg in get_mail(service):
        threadId = msg['threadId']

        for header in msg['payload']['headers']:
            if header['name'] == 'From':
                name, _, addr = re.search(r'(?:(\w+)\s+(\w+))\s+<(\w+@\w+\.\w+)>', header['value']).groups()
            elif header['name'] == 'Subject':
                subject = header['value']
        
        if addr == json.load(open('sarah.json', 'r'))['email']:
            new_msg = create_mail(addr, subject, SARAH_TEMPLATE.format(name), threadId)
        else:   
            new_msg = create_mail(addr, subject, REPLY_TEMPLATE.format(name), threadId)
        service.users().messages().send(userId = 'me', body = new_msg).execute()
    

if __name__ == '__main__':
    main()

