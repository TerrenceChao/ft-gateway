from abc import ABC, abstractmethod
from typing import Dict


class IServiceApi(ABC):
    @abstractmethod
    def get(self, url: str, params: Dict = None, headers: Dict = None):
        pass

    @abstractmethod
    def post(self, url: str, json: Dict, headers: Dict = None):
        pass

    @abstractmethod
    def post2(self, url: str, json: Dict, headers: Dict = None):
        pass

    @abstractmethod
    def put(self, url: str, json: Dict = None, headers: Dict = None):
        pass

    @abstractmethod
    def delete(self, url: str, headers: Dict = None):
        pass

    @abstractmethod
    def delete_with_statuscode(self, url: str, params: Dict = None, headers: Dict = None):
        pass
