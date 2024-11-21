class TopoNet(object):
    def __init__(self):
        self.cnet = Containernet()
        self.host_image = dimage
        self.switch_image = "docker.zhai.cm/p4lang/p4c"
        self.topos = {}
        self.topos_lock = threading.Lock()
        self.cnet.start()
        self.started = True
        self.hosts = []
        self.switches = []
        self.links = []

    def add_topo(self, topo):