from fastapi import status
from typing import Dict, Optional, Tuple
from ...domains.service_api import IServiceApi
from ...configs.exceptions import *
from ...apps.resources.handlers.http_resource import HttpResourceHandler
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


SUCCESS_CODE = "0"


class ServiceApiAdapter(IServiceApi):
    def __init__(self, connect: HttpResourceHandler):
        self.connect = connect


    """
    return result
    """
    async def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs) 
            response = await client.get(url, params=params, headers=headers)

        except Exception as e:
            log.error(f"simple_get request error, url:%s, params:%s, headers:%s, resp:%s, err:%s",
                    url, params, headers, response, e.__str__())
            raise ServerException(msg='get_connection_error')
            
        self.__status_code_validation(
            response=response,
            method='GET',
            url=url,
            body=None,
            params=params,
            headers=headers,
        )

        result = response.json()
        result = result["data"]

        return result

    """
    return result, msg, err
    """
    async def get(self, url: str, params: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[str]]:
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.get(url, params=params, headers=headers)
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
    async def get_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]]:
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.get(url, params=params, headers=headers)
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
    return result
    """
    async def simple_post(self, url: str, json: Dict, headers: Dict = None) -> (Optional[Dict[str, str]]):
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.post(url, json=json, headers=headers)

        except Exception as e:
            log.error(f"simple_post request error, url:%s, json:%s, headers:%s, resp:%s, err:%s",
                    url, json, headers, response, e.__str__())
            raise ServerException(msg='post_connection_error')
            
        self.__status_code_validation(
            response=response,
            method='POST',
            url=url,
            body=json,
            params=None,
            headers=headers,
        )

        result = response.json()
        result = result["data"]

        return result

    async def post_data(self, url: str, byte_data: bytes, headers: Dict = None) -> (Optional[Dict[str, str]]):
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.post(url, data=byte_data, headers=headers)

        except Exception as e:
            log.error(f"simple_post request error, url:%s, data:%s, headers:%s, resp:%s, err:%s",
                    url, byte_data.decode(), headers, response, e.__str__())
            raise ServerException(msg='post_connection_error')
            
        self.__status_code_validation(
            response=response,
            method='POST',
            url=url,
            body=None,
            params=None,
            headers=headers,
        )

        result = response.json()
        result = result["data"]

        return result
    
    """
    return result, msg, err
    """
    async def post(self, url: str, json: Dict, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[str]]:
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.post(url, json=json, headers=headers)
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
    async def post_with_statuscode(self, url: str, json: Dict, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]]:
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.post(url, json=json, headers=headers)
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
    return result
    """
    async def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.put(url, json=json, headers=headers)

        except Exception as e:
            log.error(f"simple_put request error, url:%s, json:%s, headers:%s, resp:%s, err:%s",
                    url, json, headers, response, e.__str__())
            raise ServerException(msg='put_connection_error')
            
        self.__status_code_validation(
            response=response,
            method='PUT',
            url=url,
            body=json,
            params=None,
            headers=headers,
        )

        result = response.json()
        result = result["data"]

        return result

    """
    return result, msg, err
    """
    async def put(self, url: str, json: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[str]]:
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.put(url, json=json, headers=headers)
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
    async def put_with_statuscode(self, url: str, json: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]]:
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.put(url, json=json, headers=headers)
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
    return result
    """
    async def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.delete(url, params=params, headers=headers)

        except Exception as e:
            log.error(f"simple_delete request error, url:%s, params:%s, headers:%s, resp:%s, err:%s",
                    url, params, headers, response, e.__str__())
            raise ServerException(msg='delete_connection_error')
            
        self.__status_code_validation(
            response=response,
            method='DEL',
            url=url,
            body=None,
            params=params,
            headers=headers,
        )

        result = response.json()
        result = result["data"]

        return result

    """
    return result, msg, err
    """
    async def delete(self, url: str, params: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[str]]:
        err: str = None
        msg: str = None
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.delete(
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
    async def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]]:
        err: str = None
        status_code: int = 500
        msg: str = None
        result = None
        response = None
        try:
            client = await self.connect.access(url=url) # self.connect.access(**kwargs)
            response = await client.delete(
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

    
    def __status_code_validation(self, response: HttpResourceHandler.Response, method: str, url: str, body: Dict = None, params: Dict = None, headers: Dict = None):
        status_code = response.status_code
        if status_code < 400:
            return
        

        # 处理错误响应
        response_json = response.json()  # 尝试解析 JSON 响应
        msg = response_json.get("msg", "unknow_error")  # 获取错误消息
        data = response_json.get("data", None)  # 获取数据

        log.error(f"service request fail, [%s]: %s, body:%s, params:%s, headers:%s, status_code:%s, msg:%s, \n response:%s", 
                method, url, body, params, headers, status_code, msg, response)

        if status_code == status.HTTP_400_BAD_REQUEST:
            raise ClientException(msg=msg, data=data)
        
        if status_code == status.HTTP_401_UNAUTHORIZED:
            raise UnauthorizedException(msg=msg, data=data)
        
        if status_code == status.HTTP_403_FORBIDDEN:
            raise ForbiddenException(msg=msg, data=data)
        
        if status_code == status.HTTP_404_NOT_FOUND:
            raise NotFoundException(msg=msg, data=data)
        
        if status_code == status.HTTP_406_NOT_ACCEPTABLE:
            raise NotAcceptableException(msg=msg, data=data)
        
        raise ServerException(msg=msg, data=data)
            

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
        yield ServiceApiAdapter()
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass
