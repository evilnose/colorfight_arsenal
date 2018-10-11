from cf_client import Game, Cell
from utils import CellIter


class DeciderAI:
    def run_state(self, g: Game) -> None:
        cell_iter = CellIter(g)
        cell_dict = collect_cells(cell_iter)
        own_cells = cell_dict[g.uid]
        own_bases = []
        for c in own_cells:
            if c.owner == g.uid:
                own_bases.append(c)
        for b in own_bases:
            if not self.fortify(b):  # If cannot fortify
                pass

    def fortify(self, base):
        pass


def collect_cells(cell_iter: CellIter) -> dict:
    res = {}
    c: Cell
    for c in cell_iter:
        if c.owner in res:
            res[c.owner].append(c)
        else:
            res[c.owner] = [c]
    return res
