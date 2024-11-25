import logging
import requests
from flask import send_from_directory
from flask_restful import Resource, request, reqparse

import const
import topo

logging.setLoggerClass(logging.Logger)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_api(api):
    api.add_resource(StartTopo, '/topo/<instance_name>')

class StartTopo(Resource):
    def get(self, instance_name):
        return {"success": True, "errorCode": "", "errorMessage": "null"}

    def post(self, instance_name):
        try:
            topo.GLOBAL_TOPO = topo.TopoNet(instance_name)
            topo_path = f"/root/instances/{instance_name}/{const.TOPO_JSON_NAME}"
            topo.GLOBAL_TOPO.build_topology_from_json(topo_path)
            topo.GLOBAL_TOPO.start()
            topo.GLOBAL_TOPO.compile_all_switch_p4()
            return {"success": True, "errorCode": "", "errorMessage": ""}
        except Exception as e:
            return {"success": False, "errorCode": "", "errorMessage": "{}".format(e)}


    def delete(self, instance_name):
        try:
            topo.GLOBAL_TOPO.stop()
            return {"success": True, "errorCode": "", "errorMessage": ""}
        except Exception as e:
            return {"success": False, "errorCode": "", "errorMessage": "{}".format(e)}
