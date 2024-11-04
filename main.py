import os

from flask import Flask
from flask_restful import Api
from mininet.net import Containernet
from mininet.cli import CLI
import logging
import route

app = Flask(__name__)
api = Api(app)
cnet = None

def main():
    cnet = Containernet()
    cnet.start()
    # register route
    route.register_api(api)

    app.run(host="::", port=25566, debug=False)

def build_topo():
    # 获取当前工作目录的绝对路径
    current_path = os.path.abspath(os.getcwd())
    logging.info(f"current work path：{current_path}")
    cnet = Containernet()
    logging.info("=====Adding Hosts=====")
    h1=cnet.addHost('h1', ip="192.168.1.1/24")
    h2=cnet.addHost('h2', ip="192.168.1.2/24")
    logging.info("=====Adding Docker Switch for p4=====")
    s1=cnet.addDocker('s1',dimage="docker.zhai.cm/p4lang/p4c")
    logging.info("=====Creating links=====")
    cnet.addLink(h1,s1)
    cnet.addLink(h2,s1)
    logging.info("=====Starting network=====")
    cnet.start()
    CLI(cnet)
    cnet.stop()

if __name__ == '__main__':
    # main()
    build_topo()