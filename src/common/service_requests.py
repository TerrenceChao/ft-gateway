import requests
import logging
from typing import Dict


log = logging.getLogger()
log.setLevel(logging.ERROR)


SUCCESS_CODE = "0"


class ServiceRequests:
    def __init__(self):
        pass
    
    def get(self, url: str, params: Dict = None, headers: Dict = None):
        err_msg: str = None
        result = None
        try:
            response = requests.get(url, params=params, headers=headers)
            result = response.json()
            if result["code"] != SUCCESS_CODE:
                err_msg = result["msg"]
                
            result = result["data"]
            
        except Exception as e:
            err_msg = e.__str__()
            
        return result, err_msg
        
    
    def post(self, url: str, json: Dict, headers: Dict = None):
        err_msg: str = None
        result = None
        try:
            response = requests.post(url, json=json, headers=headers)
            result = response.json()
            if result["code"] != SUCCESS_CODE:
                err_msg = result["msg"]
                
            result = result["data"]
            
        except Exception as e:
            err_msg = e.__str__()
            
        return result, err_msg
    
    
    def put(self, url: str, json: Dict, headers: Dict = None):
        err_msg: str = None
        result = None
        try:
            response = requests.put(url, json=json, headers=headers)
            result = response.json()
            if result["code"] != SUCCESS_CODE:
                err_msg = result["msg"]
                
            result = result["data"]
            
        except Exception as e:
            err_msg = e.__str__()
            
        return result, err_msg
    

def get_service_requests():
    try:
        service_requests = ServiceRequests()
        yield service_requests
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass