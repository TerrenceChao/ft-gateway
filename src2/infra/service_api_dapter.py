import requests as Requests
from typing import Dict, Any
from ..domains.service_api import IServiceApi
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


SUCCESS_CODE = "0"


class ServiceApiAdapter(IServiceApi):
    def __init__(self, requests: Requests):
        self.requests = requests
    
    def get(self, url: str, params: Dict = None, headers: Dict = None):
        err: str = None
        result = None
        response = None
        try:
            response = self.requests.get(url, params=params, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, self.__err_resp(result)
            
            log.info(result)
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.error(f"get request error, url:{url}, params:{params}, headers:{headers}, resp:{response}, err:{err}")
            
        return result, err
        
    
    def post(self, url: str, json: Dict, headers: Dict = None):
        err: str = None
        result = None
        response = None
        try:
            response = self.requests.post(url, json=json, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, self.__err_resp(result)
                
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.error(f"post request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")

            
        return result, err
    

    """
    return data, msg, err
    """
    def post2(self, url: str, json: Dict, headers: Dict = None):
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.post(url, json=json, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, None, self.__err_resp(result)
            
            msg = result["msg"]
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.error(f"post2 request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")
            
        return result, msg, err
    
    
    def put(self, url: str, json: Dict = None, headers: Dict = None):
        err: str = None
        result = None
        response = None
        try:
            response = self.requests.put(url, json=json, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, self.__err_resp(result)
                
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.error(f"put request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")
            
        return result, err


    def delete(self, url: str, headers: Dict = None):
        err: str = None
        result = None
        response = None
        try:
            response = self.requests.delete(url, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, self.__err_resp(result)
            
            log.info(result)
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.error(f"delete request error, url:{url}, headers:{headers}, resp:{response}, err:{err}")
            
        return result, err
    
    def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None):
        err: str = None
        msg: str = None
        result = None
        response = None
        status_code: int = 500
        try:
            response = self.requests.delete(url, params=params, headers=headers)
            result = response.json()
            status_code = response.status_code
            log.info(f"url:{url}, resp-data:{result}")
            msg = result["msg"]
            result = result["data"]
            
        except Exception as e:
            err = e.__str__()
            log.error(f"delete request error, url:{url}, headers:{headers}, resp:{response}, err:{err}")
            
        return result, msg, err, status_code


    def __err(self, resp_json):
        return not "code" in resp_json or resp_json["code"] != SUCCESS_CODE
    
    def __err_resp(self, resp_json):
        if "detail" in resp_json:
            return str(resp_json["detail"])
        if "msg" in resp_json:
            return str(resp_json["msg"])
        if "message" in resp_json:
            return str(resp_json["message"])
        
        log.error(f"cannot find err msg, resp_json:{resp_json}")
        return "service reqeust error"


def get_service_requests():
    try:
        service_requests = ServiceApiAdapter(requests)
        yield service_requests
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass