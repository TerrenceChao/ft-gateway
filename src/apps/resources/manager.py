import asyncio
from typing import Dict
from .handlers._resource import ResourceHandler
from .handlers.http_resource import HttpResourceHandler
from .handlers.cache_resource import DynamodbCacheResourceHandler
from ...configs.conf import PROBE_CYCLE_SECS
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)



class GlobalIOResourceManager:
    def __init__(self):
        self.resources: Dict[str, ResourceHandler] = {
            'http': HttpResourceHandler(),
            'ddb_cache': DynamodbCacheResourceHandler(),
        }

    def get(self, resource: str) -> ResourceHandler:
        if resource not in self.resources:
            raise ValueError(f'ResourceHandler "{resource}" not found.')
        
        return self.resources[resource]




    async def initial(self):
        for resource in self.resources.values():
            await resource.initial()

    async def probe(self):
        for resource in self.resources.values():
            try:
                if not resource.timeout():
                    log.info(f' ==> probing {resource.__class__.__name__}')
                    await resource.probe()
                else:
                    await resource.close()

            except Exception as e:
                log.error('probe error: %s', e)


    # 定期激活，維持連線和連線池
    # Regular activation to maintain connections and connection pools
    async def keeping_probe(self):
        while True:
            await asyncio.sleep(PROBE_CYCLE_SECS)
            await self.probe()
                


    async def close(self):
        for resource in self.resources.values():
            await resource.close()




io_resource_manager = GlobalIOResourceManager()
