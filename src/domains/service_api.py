from abc import ABC, abstractmethod
from typing import Dict, Union, Any, Optional, Tuple
from fastapi import Request


class IServiceApi(ABC):
    @abstractmethod
    async def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, str]]:
        pass
    
    @abstractmethod
    async def get(self, url: str, params: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[str]]:
        pass
    
    @abstractmethod
    async def get_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]]:
        pass
    
    @abstractmethod
    async def simple_post(self, url: str, json: Dict, headers: Dict = None) -> Optional[Dict[str, str]]:
        pass

    @abstractmethod
    async def post_data(self, url: str, byte_data: bytes, headers: Dict = None) -> Optional[Dict[str, str]]:
        pass
    
    @abstractmethod
    async def post(self, url: str, json: Dict, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[str]]:
        pass

    @abstractmethod
    async def post_with_statuscode(self, url: str, json: Dict, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]]:
        pass

    @abstractmethod
    async def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> Optional[Dict[str, str]]:
        pass
    
    @abstractmethod
    async def put(self, url: str, json: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[str]]:
        pass
    
    @abstractmethod
    async def put_with_statuscode(self, url: str, json: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]]:
        pass
    
    @abstractmethod
    async def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, str]]:
        pass

    @abstractmethod
    async def delete(self, url: str, params: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[str]]:
        pass

    @abstractmethod
    async def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None) -> Tuple[Optional[Dict[str, str]], Optional[str], Optional[int], Optional[str]]:
        pass
