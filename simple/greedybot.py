import logging

from cf_client import Game, Cell, CellIter
from utils import get_valid_targets


class GreedyBot:
    def __init__(self, aggression=3):
        self.game = None
        self.aggression = aggression

    def run_state(self, game: Game) -> None:
        self.game = game
        targets = get_valid_targets(game)
        targets = list(targets)
        if not targets:
            logging.warning('No valid targets')
            return
        t = sorted(targets, key=lambda c: self.cell_key(c))[-1]
        # print("Best cell is one with weight", self.cell_key(t))
        game.attack_cell(t.x, t.y)

    def cell_key(self, c: Cell) -> float:
        if c.isTaking:
            return -10000

        res = 0.
        if c.owner != 0 and c.owner != self.game.uid:
            res += self.aggression

        if c.buildType == 'base':
            if c.owner != 0 and c.owner != self.game.uid:
                res += 0.2
            res += 1
        if c.cellType == 'gold':
            res += 1.5
        elif c.cellType == 'energy':
            res += 1.5

        res -= c.takeTime ** 0.5
        return res





