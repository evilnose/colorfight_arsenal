from cf_client import Game, Cell
from utils import CellIter, get_valid_targets


class SprawlBot:
    def __init__(self, aggression=5):
        self.game = None
        self.aggression = aggression

    def run_state(self, game: Game) -> None:
        self.game = game
        targets = get_valid_targets(game)
        targets = list(targets)
        t = sorted(targets, key=lambda c: self.cell_key(c))[-1]
        game.attack_cell(t.x, t.y)
        print('Attacking cell x={}, y={}'.format(t.x, t.y))

    def cell_key(self, c: Cell) -> float:
        if c.isTaking:
            return -10000

        res = 0.
        if c.owner != 0 and c.owner != self.game.uid:
            res += self.aggression

        if c.buildType == 'base':
            if c.owner != 0 and c.owner != self.game.uid:
                res += 4
            res += 1
        if c.cellType == 'gold':
            res += 0.5
        elif c.cellType == 'energy':
            res += 1

        res -= c.takeTime ** 0.5
        return res





