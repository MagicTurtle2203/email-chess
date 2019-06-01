import base64
import random
import re
import time

from cs   import chess_io
from mail import mail
from mail import templates


def parse_mail(service, msg) -> None:
    header_dict = {header['name']:header['value'] for header in msg['payload']['headers']}
    header_dict['threadId'] = msg['threadId']

    first_name, last_name, sender = re.search(r'(?:(\w+)\s+(\w+))\s+<(\w+@\w+\.\w+)>', header_dict['From']).groups()

    if header_dict['Subject'].lower() == 'start game':
        body = base64.b64decode(msg['payload']['body']['data']).decode()

        opponent = re.search(r'(?:opponent: (\w+@\w+\.\w+))', body, re.IGNORECASE)[1]
        white = re.search(r'(?:white: (random|me|\w+@\w+\.\w+))', body, re.IGNORECASE)[1]

        black = opponent

        if white.lower() == 'random':
            white, black = random.sample([sender, opponent], k=2)
        elif white.lower() == 'me':
            white, black = sender, opponent

        reply = mail.create_mail(sender, header_dict['Subject'], templates.START_GAME_REPLY.format(opponent), header_dict)
        challenge = mail.create_mail(opponent, f"New chess challenge from {sender}!", templates.CHALLENGE_MESSAGE.format(
                opponent, f"{first_name} {last_name} ({sender})"))

        service.users().messages().send(userId='me', body=reply).execute()
        threadId = service.users().messages().send(userId='me', body=challenge).execute()['threadId']

        chess_io.create(white, black, threadId)

    else:
        message = mail.create_mail(sender, header_dict['Subject'], templates.REPLY.format(first_name), header_dict)
        service.users().messages().send(userId='me', body=message).execute()


if __name__ == '__main__':
    service = mail.get_service()

    for msg in mail.get_mail(service):
        parse_mail(service, msg)