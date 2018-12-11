import logging
import time

from cf_client import Game
# from simple.icbm import ICBM
from simple.greedybot import GreedyBot
from simple.decider import DeciderAI
from simple.turtle import Turtle
from utils import ended

HOST_URL = 'http://colorfightuw.herokuapp.com/'
SLEEP_INTERVAL = 0.1
NAMES = ['GlaDOS', 'The Terminator', 'Mark Zuckerberg', 'TOTALLY NOT A ROBOT', 'The Destroyer',
         'BetaGo', 'Wheatley', 'Garry Kasparov', 'HAL 9000', 'Frankenstein\'s Monster', 'Ultron',
         'Deep Thought', '42', 'God', 'Wall-E']


def startgame():
    print("Running greedyBot")
    g = Game(id='')
    if not g.join('BN', host_url=HOST_URL):
        raise RuntimeError('Something went wrong')
    ai = GreedyBot(aggression=2)
    # while not ended(g):
    while True:
        if g.has_valid_moves():
            ai.run_state(g)
            time.sleep(SLEEP_INTERVAL)
        g.refresh()
    logging.info('Ended.')


def startgame_turtle():
    print("Running turtle")
    g = Game(id='turtle')
    if not g.join('Thanos', host_url=HOST_URL):
        raise RuntimeError('Something went wrong')
    ai = Turtle()
    # while not ended(g):
    while True:
        ai.update_multi()
        res = ai.run_state(g)
        g.refresh()
        if res != 'fail' and res != 'base':
            time.sleep(SLEEP_INTERVAL)
    logging.info('Ended.')


if __name__ == '__main__':
    startgame_turtle()
