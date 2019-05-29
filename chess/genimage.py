import re
from PIL import Image
from pathlib import Path


BOARD_PATTERN = re.compile(r'(?:\w+\/){7}\w+')

pieces = {
    'p': Image.open(Path('images/dp.png')),
    'n': Image.open(Path('images/dn.png')),
    'b': Image.open(Path('images/db.png')),
    'r': Image.open(Path('images/dr.png')),
    'q': Image.open(Path('images/dq.png')),
    'k': Image.open(Path('images/dk.png')),
    'P': Image.open(Path('images/lp.png')),
    'N': Image.open(Path('images/ln.png')),
    'B': Image.open(Path('images/lb.png')),
    'R': Image.open(Path('images/lr.png')),
    'Q': Image.open(Path('images/lq.png')),
    'K': Image.open(Path('images/lk.png'))
}


def create_image(FEN: str) -> Image:
    board = Image.open(Path('images/board.png'))

    board_string = ''.join([' ' * int(i) if i.isdigit() else i for i in BOARD_PATTERN.search(FEN)[0].replace('/', '')])

    for idx in range(len(board_string)):
        y, x = map(lambda x: x * 100, divmod(idx, 8))
        if board_string[idx] in pieces:
            board.paste(pieces[board_string[idx]], (x, y), pieces[board_string[idx]])

    return board
