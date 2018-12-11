import logging
from enum import Enum


class Timer:
    def __init__(self, time_step, end):
        self.now = 0
        self.time_step = time_step
        self.end = end

    def reset(self):
        self.now = 0

    def tic(self):
        self.now += self.time_step

    def ended(self):
        return self.now >= self.end


class ColorFightSim:
    def __init__(self, width=30, height=30, time_step=100, end_time=120000):
        self.width = width
        self.height = height
        self.grid = [[Cell(x, y, self.timer) for x in range(self.width)] for y in range(self.height)]
        self.users = dict()
        self.last_uid = 1
        self.timer = Timer(time_step, end_time)

    def add_user(self, label):
        # TODO check grid cell and add user
        u = User(self.last_uid, label)
        self.users[self.last_uid] = u
        self.last_uid += 1

    def kill_user(self, uid):
        if uid not in self.users:
            raise ValueError('No user with uid {} exists'.format(uid))
        # TODO validate no cells exist
        del self.users[uid]

    def freeze(self):
        """
        Return a representation of the current state. Call thaw() with that as
        argument to restore the simulation.
        :return: A frozen representation of the current state
        """
        # TODO

    def thaw(self, state):
        # TODO
        pass

    def tic(self):
        self.timer.tic()
        for row in self.grid:
            for cell in row:
                cell.refresh()


class Cell:
    DEFAULT_TAKE_TIME = 2000

    class Type(Enum):
        NORMAL = 0
        GOLD = 1
        ENERGY = 2

    def __init__(self, x, y, timer, owner=0, type_=Type.NORMAL, is_base=False):
        self.x = x
        self.y = y
        self.timer = timer
        self.owner = owner
        self.type = type_
        self.is_base = is_base
        self.attacker: int = None
        self.time_occupied = None
        self.time_attacked = None
        self.take_time = Cell.DEFAULT_TAKE_TIME
        self.under_attack = False
        self.last_refresh = None

    def attack(self):
        if self.under_attack:
            logging.warning('Cannot attack: cell already under attack')
            return False
        self.time_attacked = self.now()

    def refresh(self):
        if self.last_refresh == self.now():
            return  # No refresh needed
        self.last_refresh = self.now()

        if self.time_occupied:
            self.take_time = Cell.compute_take_time(self.time_occupied, self.now())
        else:
            self.take_time = Cell.DEFAULT_TAKE_TIME

        if self.time_attacked:
            if self.timer.now - self.time_attacked >= self.take_time:
                # Attack successful
                self.owner = self.attacker
                self.time_attacked = None
                self.time_occupied = self.now()

    def now(self):
        return self.timer.now

    @staticmethod
    def compute_take_time(last_occupied, now):
        return 30 * (2 ** ((last_occupied - now) / 30.)) + 3


class User:
    def __init__(self, uid, label=''):
        self.uid = uid
        self.label = label
