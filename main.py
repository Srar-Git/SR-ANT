import os
import subprocess
import sys

from flask import Flask
from flask_restful import Api
from mininet.net import Containernet
from mininet.cli import CLI
import logging
import route

app = Flask(__name__)
api = Api(app)
cnet = None
project_path = ""
logging.setLoggerClass(logging.Logger)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    cnet = Containernet()
    cnet.start()
    # register route
    route.register_api(api)

    app.run(host="::", port=25566, debug=False)

def execute_cmd_on_controller(cmd, timeout=10):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, error = p.communicate()
    res = output.decode()
    if p.wait(timeout=timeout) != 0:
        logger.error("execute cmd %s on controller failed after time %s"%(cmd, timeout))
        raise Exception("execute cmd %s on controller failed after time %s"%(cmd, timeout))
    else:
        logger.info("execute cmd %s on controller success"%cmd)
        logger.info("result: %s"% res)

def build_topo():
    # 获取当前工作目录的绝对路径
    current_path = execute_cmd_on_controller("pwd")
    logging.info(f"current work path：{current_path}")
    cnet = Containernet()
    logging.info("=====Adding Hosts=====")
    h1 = cnet.addDocker('h1', ip="192.168.1.1/24", network_mode="none",dimage="docker.zhai.cm/p4lang/p4c")
    h2 = cnet.addDocker('h2', ip="192.168.1.2/24", network_mode="none",dimage="docker.zhai.cm/p4lang/p4c")
    logging.info("=====Adding Docker Switch for p4=====")
    s1 = cnet.addDocker('s1', dimage="docker.zhai.cm/p4lang/p4c",
                        volumes=["{}/instances/:/instances/:rw".format(project_path)])
    logging.info("=====Creating links=====")
    cnet.addLink(h1, s1)
    cnet.addLink(h2, s1)
    logging.info("=====Starting network=====")
    cnet.start()
    CLI(cnet)
    cnet.stop()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        project_path = sys.argv[1]
        build_topo()
    else:
        print("没有传入参数")

    # main()

