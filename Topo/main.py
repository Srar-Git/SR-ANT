from Topo.mininet.link import TCLink
from Topo.mininet.log import setLogLevel
from Topo.mininet.node import Controller
from Topo.switch.bmv2 import Bmv2Switch
from mininet.net import Containernet


def topology():
    net = Containernet(controller=Controller)

    # 添加控制器
    net.addController('c0')

    # 添加 bmv2 交换机
    s1 = net.addSwitch('s1', cls=Bmv2Switch, grpc_port=50051, thrift_port=9090, json_path='build/basic.json')

    # 添加 Docker 容器作为主机
    h1 = net.addDocker('h1', ip='10.0.0.1', dimage="ubuntu:latest")
    h2 = net.addDocker('h2', ip='10.0.0.2', dimage="ubuntu:latest")

    # 添加链路
    net.addLink(h1, s1, cls=TCLink)
    net.addLink(h2, s1, cls=TCLink)

    # 启动网络
    net.start()
    net.ping([h1, h2])
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()