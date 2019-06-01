import chess
import chess.pgn
import datetime
import io
import json

from pathlib import Path


PATH = Path().resolve() / 'cs' / Path('data/store.json')

STR_TO_DATE_FORMAT = r'%Y-%m-%d %H:%M:%S.%f'

GEMATRIA = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
    'j': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17, 
    'r': 18, 's': 19, 't': 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24, 'y': 25, 
    'z': 26, 'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 
    'I': 9, 'J': 10, 'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 
    'Q': 17, 'R': 18, 'S': 19, 'T': 20, 'U': 21, 'V': 22, 'W': 23, 'X': 24, 
    'Y': 25, 'Z': 26, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
    '8': 8, '9': 9
}


def create(white: str, black: str, listen: 'threadId') -> None:
    game = chess.pgn.Game()
    game.headers['Event'] = 'E-Mail Game'
    game.headers['Site'] = 'Online'
    game.headers['Date'] = datetime.date.today().strftime(r'%Y.%m.%d')
    game.headers['Round'] = '1'
    game.headers['White'] = white
    game.headers['Black'] = black

    with open(PATH, 'r+') as f:
        games = json.load(f)

        key = _hash(white, black)
        
        games[key] = {}
        games[key]['start_date'] = str(datetime.datetime.today())
        games[key]['status'] = 'waiting'
        games[key]['listen'] = listen
        games[key]['game'] = {}
        games[key]['game']['white'] = white
        games[key]['game']['black'] = black
        games[key]['game']['pgn'] = str(game)

        f.seek(0)
        json.dump(games, f)
        f.truncate()


def delete(email1: str, email2: str) -> None:
    with open(PATH, 'r+') as f:
        games = json.load(f)

        key = _hash(email1, email2)

        del games[key]

        f.seek(0)
        json.dump(games, f)
        f.truncate()


def read(email1: str, email2: str) -> chess.Board:
    with open(PATH, 'r') as f:
        games = json.load(f)

        key = _hash(email1, email2)

        pgn = io.StringIO(games[key]['pgn'])
        game = chess.pgn.read_game(pgn)

        board = game.board()

        for move in game.mainline_moves():
            board.push(move)

    return board


def write(email1: str, email2: str, board: chess.Board) -> None:
    with open(PATH, 'r+') as f:
        games = json.load(f)

        key = _hash(email1, email2)

        pgn_read = chess.pgn.read_game(io.StringIO(games[key]['pgn']))
        pgn_write = chess.pgn.Game.from_board(board)

        pgn_write.headers = pgn_read.headers
        games[key]['pgn'] = str(pgn_write)

        f.seek(0)
        json.dump(games, f)
        f.truncate()


def _hash(*args: str) -> str:
    total = 0

    com = ''.join(map(str, args))

    for char in com:
        if char in GEMATRIA:
            total += GEMATRIA[char]
        else:
            total += 1

    return str(total * len(com))

