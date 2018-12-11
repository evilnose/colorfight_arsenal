from timeit import default_timer as timer
from collections import defaultdict

import numpy as np

from cf_client import Game, Cell, CellIter


class AI:
    def run_state(self, state):
        pass


class State:
    COLUMNS = ['owner', 'type', 'time_left']

    def __init__(self, width=30, height=30):
        self.np_grid = np.zeros((height, width, len(State.COLUMNS)))


# Returns True if game has ended
def ended(g: Game) -> bool:
    players = set()
    for x in range(g.width):
        for y in range(g.height):
            c = g.get_cell(x, y)
            if c.owner != 0:
                players.add(c.owner)
    return not (g.uid in players and len(players) > 1)


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


def game_summary(game: Game):
    it = CellIter(game)
    summary = defaultdict(lambda: defaultdict(list))
    for c in it:
        owner = summary[c.owner]
        owner['all'].append(c)
        if c.isBase:
            owner['base'].append(c)
        if c.cellType == 'gold':
            owner['gold'].append(c)
        elif c.cellType == 'energy':
            owner['energy'].append(c)
        else:
            owner['normal'].append(c)

    return summary


def get_cells_relative(cell: Cell, pos_list, game: Game):
    x = cell.x
    y = cell.y
    res_list = list()
    for pos in pos_list:
        c = game.get_cell(x + pos[0], y + pos[1])
        if c:
            res_list.append(c)
    return res_list


class Timer:
    def __init__(self, wait):
        self.wait = wait
        self.__start_time = None

    def start(self):
        self.__start_time = timer()

    def ended(self):
        if not self.__start_time:
            return True
        return (timer() - self.__start_time) > self.wait

    def end_now(self):
        self.__start_time = 0


def signum(n):
    return 0 if n == 0 else int(n / abs(n))


def rotate(vec):
    if vec[0] == 0:
        return [vec, (-1, vec[1]), (1, vec[1])]
    elif vec[0] == 1:
        if vec[1] == 0:
            return [vec, (1, 1), (1, -1)]
        elif vec[1] == 1:
            return [vec, (0, 1), (1, 0)]
        else:
            return [vec, (0, -1), (1, 0)]
    else:
        if vec[1] == 0:
            return [vec, (-1, 1), (-1, -1)]
        elif vec[1] == 1:
            return [vec, (0, 1), (-1, 0)]
        else:
            return [vec, (-1, 0), (0, -1)]


def take_time(cell: Cell):
    """
    Score cells based on a lazy approach (faster to capture, the better)
    """
    return cell.takeTime


def find_closest(origin: Cell, game: Game, cond) -> (Cell, int):
    layer = 1
    while layer + 1 <= game.width and layer + 1 <= game.height:
        for x, y in get_indices(origin.x, origin.y, layer):
            if cond(game.get_cell(x, y)):
                return game.get_cell(x, y), dist(origin.x, origin.y, x, y)
        layer += 1
    return None, -1


def get_indices(x, y, l):
    res_len = l * 2 - 1
    top_down_list = list(zip(range(x - l, x + l), [y + l] * res_len)) + list(
        zip(range(x - l + 1, x + l + 1), [y - 1] * res_len))
    left_right_list = list(zip(range(y - l, y + l), [x - 1] * res_len)) + list(
        zip(range(y - l + 1, y + l + 1), [x + 1] * res_len))
    return top_down_list + left_right_list


def dist(c1, c2):
    return ((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2) ** 0.5


def find_path(s: Cell, t: Cell, path: list, game: Game):
    if not s or s in path:
        return None

    path = path + [s]

    if s.x == t.x and s.y == t.y:
        return path

    xdiff = t.x - s.x
    ydiff = t.y - s.y
    target_dir = (signum(xdiff), signum(ydiff))
    target_dirs = rotate(target_dir)  # Try two more directions that are close to target_dir
    for td in target_dirs:
        new_path = find_path(game.get_cell(int(s.x + td[0]), int(s.y + td[1])), t, path, game)
        if new_path:
            return new_path

    return None
