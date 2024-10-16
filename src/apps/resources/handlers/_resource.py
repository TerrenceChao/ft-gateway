from abc import ABC, abstractmethod


class ResourceHandler(ABC):

    @abstractmethod
    async def initial(self):
        pass

    @abstractmethod
    async def access(self, **args):
        pass

    # 定期激活，維持連線和連線池
    @abstractmethod
    async def probe(self):
        pass

    @abstractmethod
    async def close(self):
        pass