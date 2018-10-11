INPUT_WIDTH = 30
INPUT_HEIGHT = 30
N_PLAYERS = 10
INPUT_CHANNELS = 4 + N_PLAYERS
'''
Input channels encoding:
cell type (one-hot): normal, gold, energy
base type (binary): is_base
occupation status (binary): can_be_attacked
owner (one-hot): you, enemy_1, enemy_2, ... enemy_10?
n = 3 + 1 + 10(?) = 15
'''