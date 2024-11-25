import os
import subprocess
import sys

from flask import Flask
from flask_restful import Api
from mininet.net import Containernet
from mininet.cli import CLI
import logging
import route
import const

app = Flask(__name__)
api = Api(app)
cnet = None
project_path = ""
logging.setLoggerClass(logging.Logger)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)







# def build_topo():
#     # 获取当前工作目录的绝对路径
#     current_path = execute_cmd_on_controller("pwd")
#     logging.info(f"current work path：{current_path}")
#     cnet = Containernet()
#     logging.info("=====Adding Hosts=====")
#     h1 = cnet.addDocker('h1', ip="192.168.1.1/24", network_mode="none",dimage="host:latest",
#                         volumes=["{}/host_utils/:/root/:rw".format(project_path)])
#     h2 = cnet.addDocker('h2', ip="192.168.1.2/24", network_mode="none",dimage="host:latest")
#     logging.info("=====Adding Docker Switch for p4=====")
#     s1 = cnet.addDocker('s1', dimage="docker.zhai.cm/p4lang/p4c",
#                         volumes=["{}/instances/:/instances/:rw".format(project_path)])
#     logging.info("=====Creating links=====")
#     cnet.addLink(h1, s1)
#     cnet.addLink(h2, s1)
#     logging.info("=====Starting network=====")
#     cnet.start()
#     logging.info("=====Links info=====")
#     for link in cnet.links:
#         logging.info(f"nodes: {link.intf1.node}-{link.intf2.node} | intfNames: {link.intf1.name}-{link.intf2.name} | addrs: {link.intf1.mac}-{link.intf2.mac}")
#     CLI(cnet)
#     cnet.stop()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        const.PROJECT_PATH = sys.argv[1]
        route.register_api(api)
        app.run(host="::", port=25566, debug=False)
    else:
        print("没有传入参数")

    # main()

