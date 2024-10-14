import asyncio, aioboto3
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


lock = asyncio.Lock()
session = aioboto3.Session()
global dynamodb


# aioboto3
async def async_db_resource():
    try:
        async with lock:
            if dynamodb is None:
                async with session.resource('dynamodb') as db:
                    dynamodb = db
            return dynamodb
    
    except Exception as e:
        log.error(e.__str__())
        async with lock:
            session = aioboto3.Session()
            async with session.resource('dynamodb') as db:
                dynamodb = db
        return dynamodb


async def release_db_resource():
    try:
        async with lock:
            if dynamodb is None:
                return
            await dynamodb.meta.client.close()

    except Exception as e:
        log.error(e.__str__())
        return