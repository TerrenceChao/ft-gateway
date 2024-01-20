from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ICache(ABC):

    @abstractmethod
    async def get(self, key: str):
        pass

    @abstractmethod
    async def set(self, key: str, val: Any, ex: int = None):
        pass

    @abstractmethod
    async def delete(self, key: str):
        pass
