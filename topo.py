import json
import logging
import threading
from mininet.net import Containernet

import const

GLOBAL_TOPO = None


class TopoNet(object):
    def __init__(self):
        self.cnet = Containernet()
        self.topos_lock = threading.Lock()
        self.started = False
        self.hosts = {}
        self.switches = {}

    def build_topology_from_json(self, json_file):
        # 读取 JSON 文件
        with open(json_file, 'r') as f:
            topology = json.load(f)
        # 创建节点（主机和交换机）
        logging.info("=====Adding Nodes=====")
        for node in topology['nodes']:
            if node['type'] == 'host':
                # 添加主机，设置 IP
                self.add_host(node['ip'], node['name'])
                logging.info(f"added host: {node['name']}")
            elif node['type'] == 'switch':
                # 添加交换机
                self.add_switch(node['name'])
                logging.info(f"added sw: {node['name']}")

        # 创建链路
        logging.info("=====Adding Links=====")
        for link in topology['links']:
            logging.info(link['node1'])
            logging.info(link['node2'])
            logging.info(self.get_node(link['node1']))
            logging.info(self.get_node(link['node2']))
            node1 = self.get_node(link['node1'])
            node2 = self.get_node(link['node2'])
            if not node1 or not node2:  # 检查节点是否为 None
                logging.error(f"Cannot add link: {link['node1']} or {link['node2']} not found!")
                continue
            try:
                self.cnet.addLink(node1, node2)
            except Exception as e:
                logging.error(e)
            logging.info(f"added link: {link['node1']}-{link['node2']}")

    def add_host(self, ip, name):
        h = self.cnet.addDocker(name, ip=ip, network_mode="none", dimage=const.DOCKER_HOST_IMAGE,
                                volumes=["{}/host_utils/:/root/:rw".format(const.PROJECT_PATH)])
        logging.info(type(h))
        self.hosts[name] = h

    def remove_host(self, name):
        self.cnet.removeDocker(name)

    def add_switch(self, name):
        s = self.cnet.addDocker(name, dimage=const.DOCKER_SWITCH_IMAGE,
                                volumes=["{}/instances/:/instances/:rw".format(const.PROJECT_PATH)])
        self.switches[name] = s

    def remove_switch(self, name):
        self.cnet.removeDocker(name)

    def get_node(self, name):
        node = self.switches.get(name)
        if node is not None:
            return node
        node = self.hosts.get(name)
        if node is not None:
            return node
        logging.error(f"Node {name} not found in hosts or switches.")
        return None

    def start(self):
        self.cnet.start()
        logging.info("=====Links info=====")
        for link in self.cnet.links:
            logging.info(
                f"nodes: {link.intf1.node}-{link.intf2.node} | intfNames: {link.intf1.name}-{link.intf2.name} | addrs: {link.intf1.mac}-{link.intf2.mac}")

    def stop(self):
        for name, host in self.hosts.items():
            self.remove_host(name)
        for name, sw in self.switches.items():
            self.remove_switch(name)
        self.hosts.clear()
        self.switches.clear()
        self.cnet.stop()

    