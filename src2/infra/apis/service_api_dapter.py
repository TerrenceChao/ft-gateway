import requests as RequestsHTTPLibrary
from typing import Dict, Union, Any
from ...domains.service_api import IServiceApi
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


SUCCESS_CODE = "0"


class ServiceApiAdapter(IServiceApi):
    def __init__(self, requests: RequestsHTTPLibrary):
        self.requests = requests

    """
    return result, err
    """
    def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None]):
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
            log.error(
                f"get request error, url:{url}, params:{params}, headers:{headers}, resp:{response}, err:{err}")

        return result, err

    """
    return result, msg, err
    """
    def get(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.get(url, params=params, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, None, self.__err_resp(result)

            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"get request error, url:{url}, params:{params}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, err

    """
    return result, msg, status_code, err
    """
    def get_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.get(url, params=params, headers=headers)
            result = response.json()
            status_code = response.status_code
            log.info(f"url:{url}, resp-data:{result}")
            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"get_with_statuscode request error, url:{url}, params:{params}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, status_code, err

    """
    return result, err
    """
    def simple_get_list(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None]):
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
            log.error(
                f"get request error, url:{url}, params:{params}, headers:{headers}, resp:{response}, err:{err}")

        return result, err

    """
    return result, msg, err
    """
    def get_list(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.get(url, params=params, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, None, self.__err_resp(result)

            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"get request error, url:{url}, params:{params}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, err

    """
    return result, msg, status_code, err
    """
    def get_list_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.get(url, params=params, headers=headers)
            result = response.json()
            status_code = response.status_code
            log.info(f"url:{url}, resp-data:{result}")
            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"get_list_with_statuscode request error, url:{url}, params:{params}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, status_code, err

    """
    return result, err
    """
    def simple_post(self, url: str, json: Dict, headers: Dict = None) -> (Union[Any, None], Union[str, None]):
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
            log.error(
                f"post request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")

        return result, err

    """
    return result, msg, err
    """
    def post(self, url: str, json: Dict, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
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
            log.error(
                f"post request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, err

    """
    return result, msg, status_code, err
    """
    def post_with_statuscode(self, url: str, json: Dict, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.post(url, json=json, headers=headers)
            result = response.json()
            status_code = response.status_code
            log.info(f"url:{url}, resp-data:{result}")
            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"post_with_statuscode request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, status_code, err

    """
    return result, err
    """
    def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None]):
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
            log.error(
                f"simple_put request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")

        return result, err

    """
    return result, msg, err
    """
    def put(self, url: str, json: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.put(url, json=json, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, None, self.__err_resp(result)

            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"put request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, err

    """
    return result, msg, status_code, err
    """
    def put_with_statuscode(self, url: str, json: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.put(url, json=json, headers=headers)
            result = response.json()
            status_code = response.status_code
            log.info(f"url:{url}, resp-data:{result}")
            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"put_with_statuscode request error, url:{url}, req:{json}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, status_code, err

    """
    return result, err
    """
    def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None]):
        err: str = None
        result = None
        response = None
        try:
            response = self.requests.delete(
                url, params=params, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, self.__err_resp(result)

            log.info(result)
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"simple_delete request error, url:{url}, headers:{headers}, resp:{response}, err:{err}")

        return result, err

    """
    return result, msg, err
    """
    def delete(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.delete(
                url, params=params, headers=headers)
            result = response.json()
            log.info(f"url:{url}, resp-data:{result}")
            if self.__err(result):
                return None, None, self.__err_resp(result)

            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"delete request error, url:{url}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, err

    """
    return result, msg, status_code, err
    """
    def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            response = self.requests.delete(
                url, params=params, headers=headers)
            result = response.json()
            status_code = response.status_code
            log.info(f"url:{url}, resp-data:{result}")
            msg = result["msg"]
            result = result["data"]

        except Exception as e:
            err = e.__str__()
            log.error(
                f"delete_with_statuscode request error, url:{url}, headers:{headers}, resp:{response}, err:{err}")

        return result, msg, status_code, err

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
        requests_lib = RequestsHTTPLibrary
        service_requests = ServiceApiAdapter(requests_lib)
        yield service_requests
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass