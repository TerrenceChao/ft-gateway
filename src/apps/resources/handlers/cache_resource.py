import asyncio
import aioboto3
from botocore.config import Config
from ._resource import ResourceHandler
from ....configs.conf import (
    TABLE_CACHE,
    DDB_CONNECT_TIMEOUT,
    DDB_READ_TIMEOUT,
    DDB_MAX_ATTEMPTS,
)
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


ddb_config = Config(
    connect_timeout=DDB_CONNECT_TIMEOUT,
    read_timeout=DDB_READ_TIMEOUT,
    retries={'max_attempts': DDB_MAX_ATTEMPTS}
)


class DynamodbCacheResourceHandler(ResourceHandler):

    def __init__(self):
        super().__init__()
        # update max_timeout
        self.max_timeout = DDB_CONNECT_TIMEOUT

        self.lock = asyncio.Lock()
        self.dynamodb = None


    async def initial(self):
        try:
            async with self.lock:
                if self.dynamodb is None:
                    async with aioboto3.Session().resource('dynamodb', config=ddb_config) as db:
                        self.dynamodb = db
                        meta = await self.dynamodb.meta.client.describe_table(TableName=TABLE_CACHE)
                        log.info('Initial Cache[ddb] ResponseMetadata: %s', meta['ResponseMetadata'])

        except Exception as e:
            log.error(e.__str__())
            async with self.lock:
                async with aioboto3.Session().resource('dynamodb', config=ddb_config) as db:
                    self.dynamodb = db


    async def access(self, **kwargs):
        self._update_access_time()

        async with self.lock:
            if self.dynamodb is None:
                await self.initial()

            return self.dynamodb


    # 定期激活，維持連線和連線池
    # Regular activation to maintain connections and connection pools
    async def probe(self):
        try:
            # meta = await self.dynamodb.Table(TABLE_CACHE).load()  # 替換 'YourTableName' 為你的表名
            meta = await self.dynamodb.meta.client.describe_table(TableName=TABLE_CACHE)
            log.info('Cache[ddb] HTTPStatusCode: %s', meta['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            log.error(f'Cache[ddb] Client Error: %s', e.__str__())
            await self.initial()


    async def close(self):
        try:
            async with self.lock:
                if self.dynamodb is None:
                    return
                await self.dynamodb.meta.client.close()
                # log.info('Cache[ddb] client is closed')

        except Exception as e:
            log.error(e.__str__())
