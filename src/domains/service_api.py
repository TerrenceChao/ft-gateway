from abc import ABC, abstractmethod
from typing import Dict, Union, Any
from fastapi import Request


class IServiceApi(ABC):
    @abstractmethod
    def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None]):
        pass
    
    @abstractmethod
    def get(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
        pass
    
    @abstractmethod
    def get_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        pass
    
    @abstractmethod
    def simple_post(self, url: str, json: Dict, headers: Dict = None) -> (Union[Any, None]):
        pass

    @abstractmethod
    def post_data(self, url: str, byte_data: bytes, headers: Dict = None) -> (Union[Any, None]):
        pass
    
    @abstractmethod
    def post(self, url: str, json: Dict, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
        pass

    @abstractmethod
    def post_with_statuscode(self, url: str, json: Dict, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        pass

    @abstractmethod
    def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> (Union[Any, None]):
        pass
    
    @abstractmethod
    def put(self, url: str, json: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
        pass
    
    @abstractmethod
    def put_with_statuscode(self, url: str, json: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        pass
    
    @abstractmethod
    def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None]):
        pass

    @abstractmethod
    def delete(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[str, None]):
        pass

    @abstractmethod
    def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (Union[Any, None], Union[str, None], Union[int, None], Union[str, None]):
        pass
