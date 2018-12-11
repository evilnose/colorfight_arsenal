import logging
import json
from collections import defaultdict

from cf_client import Game, Cell
from utils import get_valid_targets, game_summary, signum, dist


class Turtle:
    '''TODO better base-attacking heuristics (e.g. surrounding base or not attacking one at all) and config hot-loading'''
    DEF_MULTI = {
        'dist': 5,
        'gold': 1.2,
        'energy': 1.2,
        'enemy_base': 0.65,
        'base': 0.1,
        'impatience': 2,
        'aggression': 1,
        'own_border': 0.7,
        'borders_enemy': 1,
        'enemy_at_border': 1.3,
        'build_base': False,
        'base_coord': [0, 0],
        'hunt': False,
        'special': False,
        'special_params': [],
        'bb_th': 5,
    }

    OCTANT = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def __init__(self):
        self.game = None
        self.summary = None
        self.base = None
        self.bases = []
        self.multi = Turtle.DEF_MULTI
        self.enemy_base_list = list()
        self.kill_map = defaultdict(list)

    def update_multi(self):
        try:
            with open('multi_config.json', 'r') as fp:
                self.multi = json.load(fp)
        except FileNotFoundError:
            logging.warning("Multiplier config file not found")
        except json.decoder.JSONDecodeError:
            logging.warning("JSON decode failed")

    def run_state(self, game: Game) -> str:
        self.enemy_base_list = list()
        self.kill_map = defaultdict(list)
        self.game = game
        if self.get_multi('special'):
            mp = self.get_multi('special_params')
            if len(mp) > 0:
                if mp[0] == 'b' and len(mp) == 4:
                    dr = None
                    if mp[3] == 'v':
                        dr = 'vertical'
                    elif mp[3] == 'h':
                        dr = 'horizontal'
                    elif mp[3] == 's':
                        dr = 'square'
                    if dr:
                        logging.info("Blasted")
                        self.game.blast(mp[1], mp[2], dr)
                elif mp[0] == 'm' and len(mp) == 3:
                    self.game.multi_attack(mp[1], mp[2])
                    logging.info("Multi-attacked")

        if self.get_multi('build_base'):
            co = self.multi['base_coord']
            if len(co) == 2:
                c = game.get_cell(co[0], co[1])
                if c:
                    good, _, _ = game.build_base(co[0], co[1])
                    if not good:
                        logging.warning("Did not successfully build base")
                    else:
                        logging.info("Base built!")
                        return 'base'
                else:
                    logging.warning("Coords out of bounds for base")
            else:
                logging.warning("Coords should be of length 2")
        self.summary = game_summary(game)
        self.bases = self.summary[game.uid]['base']
        if len(self.bases):
            self.base = self.bases[0]
        else:
            logging.error("No base found!")
        targets = get_valid_targets(game)
        targets = list(targets)
        if not targets:
            logging.warning('No valid targets')
            return 'fail'
        st = sorted(targets, key=lambda ce: self.cell_key(ce))
        hunting = False
        if self.get_multi('hunt') and (len(self.enemy_base_list) > 0 or len(self.kill_map) > 0):
            if len(self.kill_map) != 0:
                print("About to attack enemy base adjacent")
                t = next(iter(self.kill_map.values()))[0]
                if t.takeTime < 10:
                    hunting = True
            else:
                print("About to attack enemy base")
                t = self.enemy_base_list[0]
                if t.takeTime < 12:
                    hunting = True

        if not hunting:
            t = st[-1]

        pot_base = sorted(targets, key=lambda ce: self.dist_from_base(ce))[-1]
        if self.dist_from_base(pot_base) > self.get_multi('bb_th'):
            good, code, msg = game.build_base(pot_base.x, pot_base.y)
            if good:
                print("build base success")
            else:
                print("build base failed", msg)

        game.attack_cell(t.x, t.y)

    def cell_key(self, c: Cell) -> float:
        if c.isTaking:
            return -10000.

        res = 0.
        if c.owner != 0 and c.owner != self.game.uid:
            res += self.get_multi('aggression')

        if c.buildType == 'base':
            if c.owner != 0 and c.owner != self.game.uid:
                res += self.get_multi('enemy_base')
                self.enemy_base_list.append(c)
            else:
                res += self.get_multi('base')
        elif c.owner != self.game.uid:
            t = self.next_to_enemy_base(c)
            if t:
                self.kill_map[t.owner].append(c)
        if c.cellType == 'gold':
            res += self.get_multi('gold')
        elif c.cellType == 'energy':
            res += self.get_multi('energy')

        # x, y = (c.x - self.base.x, c.y - self.base.y)
        enemy = self.is_not_friendly(c.x, c.y)
        border = False
        borders_enemy = False
        if not enemy:
            border = any(self.is_not_friendly(c.x + dx, c.y + dy) for (dx, dy) in Turtle.OCTANT)
            borders_enemy = any(self.is_enemy(c.x + dx, c.y + dy) for (dx, dy) in Turtle.OCTANT)
            # if x == 0:
            #     if y == 0:
            #         # base
            #         border = self.is_not_friendly(c.x, c.y + 1) or self.is_not_friendly(
            #             c.x, c.y - 1) or self.is_not_friendly(c.x + 1, c.y) or self.is_not_friendly(c.x - 1, c.y)
            #         border_enemy = self.is_enemy(c.x, c.y + 1) or self.is_enemy(
            #             c.x, c.y - 1) or self.is_enemy(c.x + 1, c.y) or self.is_enemy(c.x - 1, c.y)
            #     else:
            #         border = self.is_not_friendly(c.x, c.y + signum(y))
            #         border_enemy = self.is_enemy(c.x, c.y + signum(y))
            # else:
            #     if y == 0:
            #         border = self.is_not_friendly(c.x + signum(x), c.y)
            #         border_enemy = any(self.is_enemy(c.x + dx, c.y + dy) for (dx, dy) in Turtle.OCTANT)
            #     else:
            #         border = self.is_not_friendly(c.x + signum(x), c.y) or self.is_not_friendly(c.x, c.y + signum(y))
            #         border_enemy = self.is_enemy(c.x + signum(x), c.y) or self.is_enemy(c.x, c.y + signum(y))

        if border or enemy:
            if border:
                res += self.get_multi('own_border') if not borders_enemy else self.get_multi('borders_enemy')
            else:
                res += self.get_multi('enemy_at_border')
            distances = [dist(c, b) for b in self.bases]
            average_dist = sum(distances) / len(distances)
            res += self.get_multi('dist') / (average_dist ** 10 + 0.5)

        if c.takeTime > 0:
            res -= self.get_multi('impatience') * c.takeTime
        return res

    def is_not_friendly(self, x, y):
        c = self.game.get_cell(x, y)
        if not c:
            return False
        return c.owner != self.game.uid

    def is_enemy(self, x, y):
        c = self.game.get_cell(x, y)
        if not c:
            return False
        return c.owner != self.game.uid and c.owner != 0

    def get_multi(self, pstr):
        if pstr in self.multi:
            return self.multi[pstr]
        return Turtle.DEF_MULTI[pstr]

    def next_to_enemy_base(self, c):
        for x, y in Turtle.OCTANT:
            t = self.game.get_cell(c.x + x, c.y + y)
            if t:
                for s in self.summary.values():
                    if t in s['base']:
                        return c
        return None

    def dist_from_base(self, c):
        if c.owner != self.game.uid:
            return -1
        distances = [dist(c, b) for b in self.bases]
        average_dist = sum(distances) / len(distances)
        return average_dist
