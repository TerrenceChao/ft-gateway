import time
from ...domains.cache import ICache
from ...configs.constants import SERIAL_KEY
from ...configs.exceptions import ServerException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def gen_confirm_code():
    code = int(time.time() ** 6 % 1000000)
    code = code if (code > 100000) else code + 100000
    log.info(f"confirm_code: {code}")
    return code


async def get_serial_num(cache: ICache, role_id: str):
    user = await cache.get(role_id)
    if not user or not SERIAL_KEY in user:
        log.error(f"get_serial_num fail: [user has no 'SERIAL_KEY'], role_id:%s", role_id)
        raise ServerException(msg="user has no authrozanization")

    return user[SERIAL_KEY]
