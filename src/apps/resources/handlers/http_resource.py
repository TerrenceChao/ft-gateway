import asyncio
import httpx
import json
from typing import List, Dict
from urllib.parse import urlparse
from ._resource import ResourceHandler
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class HttpResourceHandler(ResourceHandler):
    def __init__(self, domains: List[str] = [
        'https://xxt0dba048.execute-api.ap-northeast-1.amazonaws.com',
    ]):
        self.resource_lock = asyncio.Lock()
        self.locks: Dict = {domain: asyncio.Lock() for domain in domains}  # 为每个域名创建锁

        self.domain_clients: Dict = {}
        for domain in domains:
            domain = self.parse_domain(domain)
            self.domain_clients[domain] = None


    async def initial(self):
        for domain in self.domain_clients.keys():
            self.domain_clients[domain] = httpx.AsyncClient()


    async def access(self, url=None):
        if url is None:
            raise Exception('url is a must')

        domain = self.parse_domain(url)
        if not domain in self.domain_clients:
            async with self.resource_lock: # 為一開始沒有 lock 的 domain 上 IO鎖
                self.locks.update({domain: asyncio.Lock()}) # 新增 lock 給新的 domain
                self.__init_by_domain(domain)

        # async with self.locks[domain]:  # 确保对同一域名的访问是线程安全的
        client = self.domain_clients[domain]
        return client


    # 定期激活，維持連線和連線池

    async def probe(self):
        for domain, client in self.domain_clients.items():
            # TODO: 為什麼碰到 self.locks[domain] 會出錯???
            # async with self.locks[domain]:  # 使用锁来防止竞争
                try:
                    # 使用 HEAD 请求检查域名是否可达
                    response = await client.head(f'http://{domain}/')  # 发送 HEAD 请求
                    if response.status_code >= 400:
                        raise Exception(response.json())
                except Exception as e:  # 捕捉 HTTP 錯誤
                    log.error('Http Connection Error: %s', e)
                    self.__init_by_domain(domain)  # 重新建立連線


    async def close(self):
        for client in self.domain_clients.values():
            await client.aclose()
        self.domain_clients.clear()



    def __init_by_domain(self, domain: str):
        self.domain_clients[domain] = httpx.AsyncClient()

    # 從 url 解析 domain
    def parse_domain(self, url):
        return urlparse(url).netloc  # 返回解析出的 domain
    
    @classmethod
    def Response(cls):
        return httpx.Response 
