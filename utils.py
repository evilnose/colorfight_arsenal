import numpy as np
import pandas as pd

from cf_client import Game


class AI:
    def run_state(self, state):
        pass


class State:
    COLUMNS = ['owner', 'type', 'time_left']

    def __init__(self, width=30, height=30):
        self.np_grid = np.zeros((height, width, len(State.COLUMNS)))


# Returns True if game has ended
def ended(g: Game) -> bool:
    self_found = False
    enemy_found = False
    for x in range(g.width):
        for y in range(g.height):
            c = g.get_cell(x, y)
            if c.owner == 0:  # no owner, continue
                continue
            if c.owner == g.uid:  #
                if enemy_found:
                    return False  # Have cell from enemy and self
                self_found = True
            if c.owner != g.uid:
                if self_found:
                    return False
                enemy_found = True

    return True


class CellIter:
    def __init__(self, game):
        self.g = game

    def __iter__(self):
        self.x = 0
        self.y = 0
        return self

    def __next__(self):
        if self.y >= self.g.height:
            raise StopIteration()
        cell = self.g.get_cell(self.x, self.y)
        self.x += 1
        if self.x == self.g.width:
            self.x = 0
            self.y += 1

        return cell


def get_valid_targets(game):
    targets = set()

    for x in range(game.width):
        for y in range(game.height):
            c = game.get_cell(x, y)
            if c.owner == game.uid:
                targets.add(c)
                continue
            if x > 0 and game.get_cell(x - 1, y).owner == game.uid:
                targets.add(c)
                continue
            if x < game.width - 1 and game.get_cell(x + 1, y).owner == game.uid:
                targets.add(c)
                continue
            if y > 0 and game.get_cell(x, y - 1).owner == game.uid:
                targets.add(c)
                continue
            if y < game.height - 1 and game.get_cell(x, y + 1).owner == game.uid:
                targets.add(c)
                continue

    return targets
