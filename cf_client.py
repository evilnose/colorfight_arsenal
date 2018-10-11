import requests
import json
import os

from requests import HTTPError


class Cell:
    def __init__(self, cell_data):
        self.owner = cell_data['o']
        self.attacker = cell_data['a']
        self.isTaking = cell_data['c'] == 1
        self.x = cell_data['x']
        self.y = cell_data['y']
        self.occupyTime = cell_data['ot']
        self.attackTime = cell_data['at']
        self.takeTime = cell_data['t']
        self.finishTime = cell_data['f']
        self.cellType = cell_data['ct']
        self.buildType = cell_data['b']
        self.isBase = cell_data['b'] == "base"
        self.isBuilding = not cell_data['bf']
        self.buildTime = cell_data['bt']

    def __repr__(self):
        s = ""
        s += "({x}, {y}), owner is {owner}\n".format(x=self.x, y=self.y, owner=self.owner)
        if self.isTaking:
            s += "Cell is being attacked\n"
            s += "Attacker is {attacker}\n".format(attacker=self.attacker)
            s += "Attack time is {atkTime}\n".format(atkTime=self.attackTime)
            s += "Finish time is {finishTime}\n".format(finishTime=self.finishTime)
        else:
            s += "Cell is not being attacked\n"
            s += "Cell is occupied at {occupyTime}\n".format(occupyTime=self.occupyTime)
            s += "Take time is {takeTime}\n".format(takeTime=self.takeTime)
        return s


class User:
    def __init__(self, user_data):
        self.id = user_data['id']
        self.name = user_data['name']
        self.cdTime = user_data['cd_time']
        self.buildCdTime = user_data['build_cd_time']
        self.cellNum = user_data['cell_num']
        self.baseNum = user_data['base_num']
        self.goldCellNum = user_data['gold_cell_num']
        self.energyCellNum = user_data['energy_cell_num']
        if 'energy' in user_data:
            self.energy = user_data['energy']
        if 'gold' in user_data:
            self.gold = user_data['gold']

    def __repr__(self):
        return "uid: {}\nname: {}\ncd time: {}\ncell number: {}\n".format(self.id, self.name, self.cdTime, self.cellNum)


class Game:
    def __init__(self):
        self.host_url = None
        self.data = None
        self.token = ''
        self.name = ''
        self.uid = -1
        self.endTime = 0
        self.joinEndTime = 0
        self.gameId = 0
        self.users = []
        self.cellNum = 0
        self.baseNum = 0
        self.goldCellNum = 0
        self.energyCellNum = 0
        self.cdTime = 0
        self.buildCdTime = 0
        self.energy = 0
        self.gold = 0
        self.gameVersion = ''
        self.ended = False
        self.width = None
        self.height = None

    def join(self, name, host_url, password=None, force=False):
        if type(name) != str:
            raise ValueError('Your name has to be a string')
        if not host_url:
            raise ValueError('host_url cannot be None')
        self.host_url = host_url

        if not force and os.path.isfile('token'):
            with open('token') as f:
                self.token = f.readline().strip()
            data = self.check_token(self.token)
            if data:
                if name == data['name']:
                    self.name = data['name']
                    self.uid = data['uid']
            return self.refresh()

        headers = {'content-type': 'application/json'}
        data = {'name': name}
        if password:
            data['password'] = password
        r = requests.post(host_url + 'joingame', data=json.dumps(data), headers=headers)
        if r.status_code == 200:
            data = r.json()
            with open('token', 'w') as f:
                f.write(data['token'] + '\n')
            self.token = data['token']
            self.uid = data['uid']
            self.data = None
            self.refresh()
        else:
            raise HTTPError('joingame returned status code != 200: ' + r.status_code)

    def attack_cell(self, x, y, boost=False):
        if self.token != '':
            headers = {'content-type': 'application/json'}
            r = requests.post(self.host_url + 'attack',
                              data=json.dumps({'cellx': x, 'celly': y, 'boost': boost, 'token': self.token}),
                              headers=headers)
            if r.status_code == 200:
                data = r.json()
                if data['err_code'] == 0:
                    return True, None, None
                else:
                    return False, data['err_code'], data['err_msg']
            else:
                return False, None, "Server did not return correctly"
        else:
            return False, None, "You need to join the game first!"

    def build_base(self, x, y):
        if self.token != '':
            headers = {'content-type': 'application/json'}
            r = requests.post(self.host_url + 'buildbase', data=json.dumps({'cellx': x, 'celly': y, 'token': self.token}),
                              headers=headers)
            if r.status_code == 200:
                data = r.json()
                if data['err_code'] == 0:
                    return True, None, None
                else:
                    return False, data['err_code'], data['err_msg']
            else:
                return False, None, "Server did not return correctly, status_code ", r.status_code
        else:
            return False, None, "You need to join the game first!"

    def blast(self, x, y, direction):
        if self.token != '':
            if direction not in ["square", "vertical", "horizontal"]:
                return False, None, "Wrong direction!"
            headers = {'content-type': 'application/json'}
            r = requests.post(self.host_url + 'blast',
                              data=json.dumps({'cellx': x, 'celly': y, 'token': self.token, 'direction': direction}),
                              headers=headers)
            if r.status_code == 200:
                data = r.json()
                if data['err_code'] == 0:
                    return True, None, None
                else:
                    return False, data['err_code'], data['err_msg']
            else:
                return False, None, "Server did not return correctly, status_code ", r.status_code
        else:
            return False, None, "You need to join the game first!"

    def multi_attack(self, x, y):
        if self.token != '':
            headers = {'content-type': 'application/json'}
            r = requests.post(self.host_url + 'multiattack', data=json.dumps({'cellx': x, 'celly': y, 'token': self.token}),
                              headers=headers)
            if r.status_code == 200:
                data = r.json()
                if data['err_code'] == 0:
                    return True, None, None
                else:
                    return False, data['err_code'], data['err_msg']
            else:
                return False, None, "Server did not return correctly, status_code ", r.status_code
        else:
            return False, None, "You need to join the game first!"

    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            c = Cell(self.data['cells'][x + y * self.width])
            return c
        return None

    @staticmethod
    def get_take_time(time_diff):
        if time_diff <= 0:
            return 33
        return 30 * (2 ** (-time_diff / 30.0)) + 3

    def refresh_users(self, user_data_list):
        self.users = []
        for userData in user_data_list:
            u = User(userData)
            self.users.append(u)
            if u.id == self.uid:
                self.gold = u.gold
                self.energy = u.energy
                self.cdTime = u.cdTime
                self.buildCdTime = u.buildCdTime
                self.cellNum = u.cellNum
                self.baseNum = u.baseNum
                self.goldCellNum = u.goldCellNum
                self.energyCellNum = u.energyCellNum
        self.users.sort(key=lambda x: x.cellNum, reverse=True)

    def refresh(self):
        headers = {'content-type': 'application/json'}
        if self.data is None:
            r = requests.post(self.host_url + 'getgameinfo', data=json.dumps({"protocol": 2}), headers=headers)
            if r.status_code == 200:
                self.data = r.json()
                self.width = self.data['info']['width']
                self.height = self.data['info']['height']
                self.currTime = self.data['info']['time']
                self.endTime = self.data['info']['end_time']
                self.joinEndTime = self.data['info']['join_end_time']
                self.gameId = self.data['info']['game_id']
                self.lastUpdate = self.currTime
                self.refresh_users(self.data['users'])
            else:
                return False
        else:
            r = requests.post(self.host_url + 'getgameinfo', data=json.dumps({"protocol": 1, "timeAfter": self.lastUpdate}),
                              headers=headers)
            if r.status_code == 200:
                d = r.json()
                self.data['info'] = d['info']
                self.data['users'] = d['users']
                self.width = d['info']['width']
                self.height = d['info']['height']
                self.currTime = d['info']['time']
                self.endTime = self.data['info']['end_time']
                self.joinEndTime = self.data['info']['join_end_time']
                self.gameId = self.data['info']['game_id']
                self.lastUpdate = self.currTime
                self.refresh_users(self.data['users'])
                for c in d['cells']:
                    cid = c['x'] + c['y'] * self.width
                    self.data['cells'][cid] = c
                for cell in self.data['cells']:
                    if cell['c'] == 1:
                        cell['t'] = -1
                    else:
                        if cell['o'] == 0:
                            cell['t'] = 2
                        else:
                            cell['t'] = self.get_take_time(self.currTime - cell['ot'])
            else:
                return False
        return True


    def check_token(self, token):
        headers = {'content-type': 'application/json'}
        r = requests.post(self.host_url + 'checktoken', data=json.dumps({'token': token}), headers=headers)
        if r.status_code == 200:
            return r.json()
        return None
