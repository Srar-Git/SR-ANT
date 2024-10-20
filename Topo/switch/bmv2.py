import os

from Topo.mininet.node import Switch

class Bmv2Switch(Switch):
    def __init__(self, name, sw_path='simple_switch_grpc', json_path=None,
                 grpc_port=None, thrift_port=None, pcap_dump=False, **kwargs):
        Switch.__init__(self, name, **kwargs)
        self.sw_path = sw_path
        self.json_path = json_path
        self.grpc_port = grpc_port
        self.thrift_port = thrift_port
        self.pcap_dump = pcap_dump

    def start(self, controllers):
        # 启动 bmv2 交换机进程
        cmd = '{} --device-id {} --log-level debug'.format(self.sw_path, self.grpc_port)
        if self.json_path:
            cmd += ' -- --grpc-server-addr 0.0.0.0:{}'.format(self.grpc_port)
            cmd += ' --thrift-port {}'.format(self.thrift_port)
            if self.pcap_dump:
                cmd += ' --pcap-dump'
            os.system(cmd + ' &')

    def stop(self):
        # 停止 bmv2 交换机进程
        os.system('pkill -f {}'.format(self.sw_path))