from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ICache(ABC):

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, val: Any, ex: int = None):
        pass
