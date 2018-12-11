from sim.backend import ColorFightSim


class ColorFightClient:
    def __init__(self, label):
        if not label:
            raise ValueError('Client label should not be None')
        self.label = label
        self.host: ColorFightSim = None

    def bind_host(self, host):
        self.host = host

    def join(self):
        if not self.host:
            raise ValueError('You have not specified a host')
        return self.host.add_user(self.label)


