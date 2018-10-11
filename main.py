import time

from cf_client import Game
from simple.sprawlbot import SprawlBot
from simple.decider import DeciderAI
from utils import ended

HOST_URL = 'http://colorfightuw.herokuapp.com/'
SLEEP_INTERVAL = 0.5


def startgame():
    g = Game()
    g.join('Lazy Boy', host_url=HOST_URL)
    ai = SprawlBot(aggression=6)
    while not ended(g):
        ai.run_state(g)
        g.refresh()
        time.sleep(SLEEP_INTERVAL)


if __name__ == '__main__':
    startgame()
