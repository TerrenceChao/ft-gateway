from abc import abstractmethod
from typing import Dict, List, Any, Optional


class Cache:

    @abstractmethod
    def get(self, key: str):
        pass
    
    @abstractmethod
    def set(self, key: str, val: Any, ex: int = None):
        pass
