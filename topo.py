import json
import logging
import re
import threading
import time

from mininet.net import Containernet

import const
import controller
from main import logger

GLOBAL_TOPO = None


class Link(object):
    def __init__(self, node1, node2, port1=None, port2=None, mac1=None, mac2=None, bw=0):
        self.node1 = node1
        self.node2 = node2
        self.port1 = int(port1)
        self.port2 = int(port2)
        self.mac1 = mac1
        self.mac2 = mac2
        self.bw = bw


class Bmv2Switch(object):
    def __init__(self, name, p4, intfs):
        self.name = name
        self.p4 = p4
        self.intfs = intfs

    def execute_cmd(self, topo, cmd, popen=False):
        node = topo.get_node(self.name)
        if popen:
            node.popen(cmd)
            logger.info("execute popen cmd %s on node %s" % (cmd, node.name))
            return None
        else:
            res = node.cmd(cmd)
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            res = ansi_escape.sub('', res)
            res = re.sub(r'\r', '', res)
            logger.info("execute cmd %s on node %s, res %s" % (cmd, node.name, res))
            return res

    def start_bmv2(self, topo):
        cmd = "simple_switch -L debug"
        for port_num, intf_name in self.intfs.items():
            cmd += f" -i {port_num}@{self.name}-{intf_name}"
        cmd += f" --thrift-port 9191 --log-file /instances/{topo.instance_name}/bmv2_{self.name}.log /instances/{topo.instance_name}/p4/{self.p4}.json"
        # cmd += f" > /instances/{topo.instance_name}/bmv2_{self.name}.log 2>&1 &"
        self.execute_cmd(topo, cmd, popen=True)

    def load_runtime(self, topo):
        cmd = f"simple_switch_CLI --thrift-port 9191 < /instances/{topo.instance_name}/run_time/{self.name}.txt"
        self.execute_cmd(topo, cmd, popen=False)



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
        self.mini_links = {}
        # Bmv2Switch
        self.switches = {}
        # Host
        self.hosts = {}
        self.links = {}
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
                intf_list = node['intfs']
                intfs = {}
                for i in intf_list:
                    num = i.split(":")[0]
                    eth = i.split(":")[1]
                    intfs[num] = eth
                s = Bmv2Switch(node['name'], node['p4'], intfs)
                self.add_switch(s)
                logging.info(f"added sw: {node['name']}")

        logging.info("=====Adding Links=====")
        for link in self.topology['links']:
            node1 = self.get_node(link['node1'])
            port1 = link['port1']
            port2 = link['port2']
            mac1 = link['mac1']
            mac2 = link['mac2']
            node2 = self.get_node(link['node2'])
            if not node1 or not node2 or not port1 or not port2:
                logging.error(f"Cannot add link: {link['node1']} or {link['node2']} not found!")
                continue
            try:
                l = Link(node1, node2, port1=port1, port2=port2, mac1=mac1, mac2=mac2)
                self.add_link(l)
                # self.cnet.addLink(node1, node2)
            except Exception as e:
                logging.error(e)
            logging.info(f"added link: {link['node1']}-{link['node2']}")

    def compile_all_switch_p4(self):
        for name, sw in self.switches.items():
            p4 = sw.p4
            sw.execute_cmd(self,
                           f"p4c-bm2-ss --p4v 16 /instances/{self.instance_name}/p4/{p4}.p4 -o /instances/{self.instance_name}/p4/{p4}.json")
            sw.start_bmv2(self)
            time.sleep(5)
            sw.load_runtime(self)

    def add_host(self, host):
        h = self.cnet.addDocker(host.name, ip=host.ip, network_mode="none", dimage=const.DOCKER_HOST_IMAGE,
                                volumes=["{}/host_utils/:/root/:rw".format(const.PROJECT_PATH)])
        logging.info(type(h))
        self.mini_hosts[host.name] = h
        self.hosts[host.name] = host

    def remove_host(self, name):
        self.cnet.removeDocker(name)

    def add_switch(self, switch):
        s = self.cnet.addDocker(switch.name, dimage=const.DOCKER_SWITCH_IMAGE, network_mode="none",
                                volumes=["{}/instances/:/instances/:rw".format(const.PROJECT_PATH)])
        self.mini_switches[switch.name] = s
        self.switches[switch.name] = switch

    def add_link(self, link):
        # intf1_params = {}
        # intf2_params = {}
        # if link.mac1:
        #     intf1_params['mac1'] = link.mac1
        # if link.mac2:
        #     intf2_params['mac2'] = link.mac2
        l = self.cnet.addLink(
            link.node1,
            link.node2,
            port1=link.port1,
            port2=link.port2,
            addr1=link.mac1,
            addr2=link.mac2
        )
        # l = self.cnet.addLink(link.node1, link.node2, port1=link.port1, port2=link.port2, mac1=link.mac1, mac2=link.mac2)
        # l = self.cnet.addLink(link.node1, link.node2)
        self.mini_links[f"{link.node1}-{link.node2}"] = l
        self.links[f"{link.node1}-{link.node2}"] = link

    def remove_switch(self, name):
        sw = self.switches.get(name)
        sw.execute_cmd(self, f"rm /instances/{self.instance_name}/p4/{sw.p4}.json")
        sw.execute_cmd(self, f"rm /instances/{self.instance_name}/bmv2_{sw.name}.log.txt")
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
