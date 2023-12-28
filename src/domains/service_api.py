from abc import ABC, abstractmethod
from typing import Dict, Union, Any, Optional
from fastapi import Request


class IServiceApi(ABC):
    @abstractmethod
    def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        pass
    
    @abstractmethod
    def get(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]], Optional[str], Optional[str]):
        pass
    
    @abstractmethod
    def get_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        pass
    
    @abstractmethod
    def simple_post(self, url: str, json: Dict, headers: Dict = None) -> (Optional[Dict[str, str]]):
        pass

    @abstractmethod
    def post_data(self, url: str, byte_data: bytes, headers: Dict = None) -> (Optional[Dict[str, str]]):
        pass
    
    @abstractmethod
    def post(self, url: str, json: Dict, headers: Dict = None) -> (Optional[Dict[str, str]], Optional[str], Optional[str]):
        pass

    @abstractmethod
    def post_with_statuscode(self, url: str, json: Dict, headers: Dict = None) -> (Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        pass

    @abstractmethod
    def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        pass
    
    @abstractmethod
    def put(self, url: str, json: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]], Optional[str], Optional[str]):
        pass
    
    @abstractmethod
    def put_with_statuscode(self, url: str, json: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        pass
    
    @abstractmethod
    def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]]):
        pass

    @abstractmethod
    def delete(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]], Optional[str], Optional[str]):
        pass

    @abstractmethod
    def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> (Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]):
        pass
