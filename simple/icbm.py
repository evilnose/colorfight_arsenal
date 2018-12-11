import logging
from enum import Enum

from cf_client import Cell
from utils import game_summary, get_cells_relative, Timer, signum, rotate, take_time, find_path


class Stage(Enum):
    SURVIVE = 0  # Survival stage: few (or weak) cells around base; need to surround base
    RELOCATE = 1  # Relocation stage: move to the edge/corner for better defense
    REINFORCE = 2  # Reinforce territories
    MINE = 3  # Find and occupy special cells (gold/energy)
    EXPAND = 4  # Expand for points and get in offensive
    SURROUND = 5  # Get into the strategic position for an attack (i.e. surround enemy cells(
    ATTACK = 6  # Attack enemy cells
    EXTERMINATE = 7  # Higher aggressiveness than attacking for finishing off enemies
    POINT_CRUNCH = 8  # End game attempt at getting as many cells as possible (and defending weak cells)


class ICBM:
    PROTECT_PATIENCE = 10  # Max take time to protect base
    PROTECT_ANXIETY = 70  # Only when safety score exceeds this, the base is deemed safe
    BASE_AREA = [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 2), (2, 0), (-2, 0), (0, -2)]
    PATH_REFRESH_INTERVAL = 5  # Re-compute path every 5 seconds
    # Maximum time allowed for relocation(should be set longer than preferred, since time estimation will overshoot)
    MAX_RELOC_TIME = 60

    def __init__(self):
        self.game = None
        self.summary = None
        self.reloc_path = None
        self.relocation_timer = Timer(5)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    def run_state(self, game):
        """
        TODO relocate only when nearby enemies are strong; if there are nearby enemies that are weak,
        TODO attack them. Also, when relocating, use a special tree structure (special as in not too sparse)

        TODO also take remaining game time as input (e.g. lots of time = survive and maintain; moderate amt. of time
        TODO = relocation and mining; low smt. of time means expansion and attacking
        """
        if not self.relocation_timer.ended():
            if len(self.reloc_path):
                self.attack(self.reloc_path.pop(0))
                return
            else:
                self.relocation_timer.end_now()

        self.game = game
        self.summary = game_summary(game)
        own_bases = self.summary[game.uid]['base']
        if len(own_bases) == 1:
            if not self.is_base_safe(own_bases[0]):
                if self.protect(own_bases[0]):
                    logging.info('Base protected.')
                    return
        elif len(own_bases) > 1:
            safe_bases = 0
            for b in own_bases:
                if self.is_base_safe(b):
                    safe_bases += 1
            if safe_bases == 0:
                if self.protect(own_bases[0]):
                    logging.info('Base protected.')
                    return

        # Base == 0 (not enabled) also ends up here
        if self.relocate():
            logging.info('Relocation step done.')
            return

    def relocate(self):
        # Base needs no protection; onto the next stage: relocate
        result, extremes = self.relocated()
        if result:
            logging.info('Relocation not required. Continuing...')
            return False  # No action need to be performed
        # Need to relocate
        min_cell = None
        min_dist = 100
        min_key = None
        for k in extremes.keys():
            if k == 'max_x':
                dist = self.game.width - 1 - extremes[k][0]
            elif k == 'max_y':
                dist = self.game.height - 1 - extremes[k][0]
            else:
                dist = extremes[k][0]
            if dist < min_dist:
                min_dist = dist
                min_cell = extremes[k][1]
                min_key = k
        if min_key == 'min_x':
            target = self.game.get_cell(0, min_cell.y)
        elif min_key == 'max_x':
            target = self.game.get_cell(self.game.width - 1, min_cell.y)
        elif min_key == 'min_y':
            target = self.game.get_cell(min_cell.x, 0)
        else:
            target = self.game.get_cell(min_cell.x, self.game.height - 1)
        planned = self.colonize(target, min_cell, 3, min_breath=3)
        if planned:
            return self.attack(self.reloc_path.pop(0))
        # Colonization planning skipped or failed

    def attack(self, cell: Cell):
        if not cell:
            return False
        return self.game.attack_cell(cell.x, cell.y)

    def colonize(self, target_cell, starting_cell, breadth, min_breath=1):
        p = find_path(starting_cell, target_cell, [], self.game)
        if not p or len(p) <= 1:
            return False
        self.reloc_path = p[1:]  # First cell is already owned, so skip
        self.relocation_timer.start()
        return True

    def is_base_safe(self, base):
        safety_score = 0
        cells_to_add = get_cells_relative(base, ICBM.BASE_AREA, self.game)
        for c in cells_to_add:
            if c.owner == self.game.uid:
                safety_score += c.takeTime
            elif c.owner != 0:
                safety_score -= c.takeTime
        return safety_score >= ICBM.PROTECT_ANXIETY

    def protect(self, base):
        cells_to_visit = get_cells_relative(base, ICBM.BASE_AREA, self.game)
        cells_to_visit.sort(key=take_time)
        target = sorted(cells_to_visit, key=take_time)[0]
        if target.takeTime >= ICBM.PROTECT_PATIENCE:
            return False
        return self.game.attack_cell(target)[0]

    def relocated(self):
        own_cells = self.summary[self.game.uid]['all']
        extremes = dict()
        extremes['min_x'] = extremes['min_y'] = (100, None)
        extremes['max_x'] = extremes['max_y'] = (-1, None)

        for c in own_cells:
            if c.x < extremes['min_x'][0]:
                extremes['min_x'] = (c.x, c)
            elif c.x > extremes['max_x'][0]:
                extremes['max_x'] = (c.x, c)
            if c.y < extremes['min_y'][0]:
                extremes['min_y'] = (c.y, c)
            elif c.y > extremes['max_y'][0]:
                extremes['max_y'] = (c.y, c)

        # Return whether any of our cell is on baseline
        return (extremes['min_x'][0] == 0 or extremes['min_y'][0] == 0 or
                extremes['max_x'][0] == self.game.width - 1 or extremes['max_y'][0] == self.game.height - 1), extremes


