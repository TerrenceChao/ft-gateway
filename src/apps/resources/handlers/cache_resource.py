import asyncio
import aioboto3
from ._resource import ResourceHandler
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class DynamodbCacheResourceHandler(ResourceHandler):

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.lock = asyncio.Lock()
        self.dynamodb = None


    async def initial(self):
        try:
            async with self.lock:
                async with aioboto3.Session().resource('dynamodb') as db:
                    self.dynamodb = db

        except Exception as e:
            log.error(e.__str__())
            async with self.lock:
                self.dynamodb = None
                async with aioboto3.Session().resource('dynamodb') as db:
                    self.dynamodb = db

            return self.dynamodb

    async def access(self, **args):
        return self.dynamodb

    # 定期激活，維持連線和連線池
    async def probe(self):
        try:
            # meta = await self.dynamodb.Table(self.table_name).load()  # 替換 'YourTableName' 為你的表名
            meta = await self.dynamodb.meta.client.describe_table(TableName=self.table_name)
            # log.info('cache meta: %s', meta)
        except Exception as e:
            log.error(f'Cache Connection Error: %s', e.__str__())
            await self.initial()


    async def close(self):
        try:
            async with self.lock:
                if self.dynamodb is None:
                    return
                await self.dynamodb.meta.client.close()
                self.dynamodb = None

        except Exception as e:
            log.error(e.__str__())
