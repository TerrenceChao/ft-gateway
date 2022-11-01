import requests
import logging as log
from typing import Dict

log.basicConfig(filemode='w', level=log.INFO)


SUCCESS_CODE = "0"


class ServiceRequests:
    def __init__(self):
        pass
    
    def get(self, url: str, params: Dict = None, headers: Dict = None):
        err: str = None
        result = None
        try:
            response = requests.get(url, params=params, headers=headers)
            result = response.json()
            if "detail" in result:
                return None, result["detail"]
            
            log.info(result)
            if result["code"] != SUCCESS_CODE:
                err = result["msg"]
                
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.error(f'get request error, url:{url}, params:{params}, headers:{headers}, err:{err}')
            
        return result, err
        
    
    def post(self, url: str, json: Dict, headers: Dict = None):
        err: str = None
        result = None
        try:
            response = requests.post(url, json=json, headers=headers)
            result = response.json()
            if "detail" in result:
                return None, result["detail"]
            
            if result["code"] != SUCCESS_CODE:
                err = result["msg"]
                
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.error(f'post request error, url:{url}, json:{json}, headers:{headers}, err:{err}')

            
        return result, err
    

    """
    return data, msg, err
    """
    def post2(self, url: str, json: Dict, headers: Dict = None):
        err: str = None
        msg: str = None
        result = None
        try:
            response = requests.post(url, json=json, headers=headers)
            result = response.json()
            if "detail" in result:
                return None, result["detail"]
            
            if result["code"] != SUCCESS_CODE:
                err = result["msg"]
                
            msg = result["msg"]
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.info(f'post2 request error, url:{url}, json:{json}, headers:{headers}, err:{err}')
            
        return result, msg, err
    
    
    def put(self, url: str, json: Dict = None, headers: Dict = None):
        err: str = None
        result = None
        try:
            response = requests.put(url, json=json, headers=headers)
            result = response.json()
            if "detail" in result:
                return None, result["detail"]
            
            if result["code"] != SUCCESS_CODE:
                err = result["msg"]
                
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.info(f'put request error, url:{url}, json:{json}, headers:{headers}, err:{err}')
            
        return result, err
    

def get_service_requests():
    try:
        service_requests = ServiceRequests()
        yield service_requests
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass