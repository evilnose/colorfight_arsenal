from cf_client import Game
from utils import game_summary, take_time, find_closest


class SpiderBot:
    """
    Stages:
    * BRANCH_OUT
    * ENCLOSE
    * MAINTAIN
    """
    MAINTENANCE_THRESHOLD = 10
    MAINTENANCE_TIME_THRESHOLD = 10

    def run_state(self, game: Game):
        self.game = game
        self.summary = game_summary(game)
        if self.maintain():
            return  # Maintenance complete

    def maintain(self):
        own_cells = self.summary[self.game.uid]['all']
        own_cells.sort(key=take_time)
        for oc in own_cells:
            if oc.takeTime > SpiderBot.MAINTENANCE_TIME_THRESHOLD:
                return False
            cell, dist = find_closest(oc, self.game, lambda c: c and (c.owner != self.game.uid))
