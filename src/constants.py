import os

LOGS_DIR = os.getcwd().replace(os.sep, '/') + "/logs/"

SOCKET_CONST = [
    'join-room',
    'receiver-card',
    'first-player',
    'color-of-wild',
    'shuffle-wild',
    'next-player',
    'play-card',
    'draw-card',
    'play-draw-card',
    'challenge',
    'public-card',
    #    'say-uno-and-play-card',
    #    'say-uno-and-play-draw-card',
    'pointed-not-say-uno',
    'special-logic',
    'finish-turn',
    'finish-game'
]
