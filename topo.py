import json
import logging
import re
import threading
from mininet.net import Containernet

import const
import controller
from main import logger

GLOBAL_TOPO = None



class Bmv2Switch(object):
    def __init__(self, name, p4):
        self.name = name
        self.p4 = p4

    def execute_cmd(self, topo, cmd):
        node = topo.get_node(self.name)
        res = node.cmd(cmd)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        res = ansi_escape.sub('', res)
        res = re.sub(r'\r', '', res)
        logger.info("execute cmd %s on node %s, res %s" % (cmd, node.name, res))
        return res

    def start_bmv2(self, topo):
        self.execute_cmd(topo, "simple_switch -i 1@s1-eth0 -i 2@s1-eth1 --thrift-port 9191 layer_two.json")
        node = topo.get_node(self.name)
        res = node.cmd(cmd)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        res = ansi_escape.sub('', res)
        res = re.sub(r'\r', '', res)
        logger.info("execute cmd %s on node %s, res %s" % (cmd, node.name, res))
        return res

class Host(object):
    def __init__(self, name, ip, ipv6=None):
        self.name = name
        self.ip = ip
        self.ipv6 = ipv6


class TopoNet(object):
    def __init__(self, instance_name):
        self.instance_name = instance_name
        self.cnet = Containernet()
        self.topos_lock = threading.Lock()
        self.started = False
        self.mini_hosts = {}
        self.mini_switches = {}
        # Bmv2Switch
        self.switches = {}
        # Host
        self.hosts = {}
        self.topology = None

    def build_topology_from_json(self, json_file):
        with open(json_file, 'r') as f:
            self.topology = json.load(f)
        logging.info("=====Adding Nodes=====")
        for node in self.topology['nodes']:
            if node['type'] == 'host':
                h = Host(node['name'], node['ip'])
                self.add_host(h)
                logging.info(f"added host: {node['name']}")
            elif node['type'] == 'switch':
                s = Bmv2Switch(node['name'], node['p4'])
                self.add_switch(s)
                logging.info(f"added sw: {node['name']}")

        logging.info("=====Adding Links=====")
        for link in self.topology['links']:
            logging.info(link['node1'])
            logging.info(link['node2'])
            logging.info(self.get_node(link['node1']))
            logging.info(self.get_node(link['node2']))
            node1 = self.get_node(link['node1'])
            node2 = self.get_node(link['node2'])
            if not node1 or not node2:
                logging.error(f"Cannot add link: {link['node1']} or {link['node2']} not found!")
                continue
            try:
                self.cnet.addLink(node1, node2)
            except Exception as e:
                logging.error(e)
            logging.info(f"added link: {link['node1']}-{link['node2']}")

    def compile_all_switch_p4(self):
        for name, sw in self.switches.items():
            p4 = sw.p4
            sw.execute_cmd(self, f"p4c-bm2-ss --p4v 16 /instances/{self.instance_name}/p4/{p4}.p4 -o /instances/{self.instance_name}/p4/{p4}.json")

    def add_host(self, host):
        h = self.cnet.addDocker(host.name, ip=host.ip, network_mode="none", dimage=const.DOCKER_HOST_IMAGE,
                                volumes=["{}/host_utils/:/root/:rw".format(const.PROJECT_PATH)])
        logging.info(type(h))
        self.mini_hosts[host.name] = h
        self.hosts[host.name] = host

    def remove_host(self, name):
        self.cnet.removeDocker(name)

    def add_switch(self, switch):
        s = self.cnet.addDocker(switch.name, dimage=const.DOCKER_SWITCH_IMAGE,
                                volumes=["{}/instances/:/instances/:rw".format(const.PROJECT_PATH)])
        self.mini_switches[switch.name] = s
        self.switches[switch.name] = switch

    def remove_switch(self, name):
        self.cnet.removeDocker(name)

    def get_node(self, name):
        node = self.mini_switches.get(name)
        if node is not None:
            return node
        node = self.mini_hosts.get(name)
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
        for name, host in self.mini_hosts.items():
            self.remove_host(name)
        for name, sw in self.mini_switches.items():
            self.remove_switch(name)
        self.mini_hosts.clear()
        self.mini_switches.clear()
        self.cnet.stop()
