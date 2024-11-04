import logging
import requests
from flask import send_from_directory
from flask_restful import Resource, request, reqparse

logging.setLoggerClass(logging.Logger)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_api(api):
    api.add_resource(AddBmv2SwitchApi, '/topo/addBmv2Switch')

class AddBmv2SwitchApi(Resource):
    def get(self):
        return {"success": True, "errorCode": "", "errorMessage": "null"}

    def post(self):
        return {"success": True, "errorCode": "", "errorMessage": "null"}

    def delete(self):
        return {"success": True, "errorCode": "", "errorMessage": "null"}
